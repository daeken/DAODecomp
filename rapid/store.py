"""Durable local queue and append-only shared request accounting."""
import json
from contextlib import closing
from pathlib import Path
import sqlite3
import time
import uuid

class Store:
    def __init__(self, root):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.db=sqlite3.connect(self.root/'queue.sqlite3',timeout=30)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.executescript('''CREATE TABLE IF NOT EXISTS batches(id TEXT PRIMARY KEY,state TEXT NOT NULL,functions TEXT NOT NULL,request_id TEXT,error TEXT,created REAL NOT NULL,finished REAL);
        CREATE TABLE IF NOT EXISTS identities(rva INTEGER PRIMARY KEY,batch TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);''')
        self.db.execute("INSERT OR IGNORE INTO meta VALUES('paused','0')"); self.db.commit()
    def close(self):
        self.db.close()
    def __del__(self):
        try: self.db.close()
        except Exception: pass
    def add(self, batch, functions):
        try:
            with self.db:
                self.db.execute('INSERT INTO batches(id,state,functions,created) VALUES(?,?,?,?)',(batch,'pending',json.dumps(functions),time.time()))
                self.db.executemany('INSERT INTO identities VALUES(?,?)',[(r,batch) for r in functions])
            return True
        except sqlite3.IntegrityError: return False
    def paused(self): return self.db.execute("SELECT value FROM meta WHERE key='paused'").fetchone()[0]=='1'
    def pause(self,value=True):
        with self.db: self.db.execute("UPDATE meta SET value=? WHERE key='paused'",('1' if value else '0',))
    def next(self):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row=None if self.paused() else self.db.execute("SELECT id FROM batches WHERE state='pending' ORDER BY created,id LIMIT 1").fetchone()
            if row: self.db.execute("UPDATE batches SET state='claimed' WHERE id=? AND state='pending'",row)
            self.db.commit(); return row[0] if row else None
        except BaseException: self.db.rollback(); raise
    def finish(self,batch,state,error=None):
        with self.db: self.db.execute('UPDATE batches SET state=?,error=?,finished=? WHERE id=?',(state,error,time.time(),batch))
    def request(self,batch,request_id):
        with self.db: self.db.execute('UPDATE batches SET request_id=? WHERE id=?',(request_id,batch))
    def reconcile(self):
        # Single-owner runtime calls this only after acquiring its flock.
        for batch, in self.db.execute("SELECT id FROM batches WHERE state='claimed'").fetchall():
            result=self.root/'batches'/batch/'result.json'
            value=json.loads(result.read_text()) if result.exists() else {}
            if value.get('final_record') is True:
                self.finish(batch,'complete' if value.get('outcome')=='success' else 'error','reconciled_retained_result')
            else: self.finish(batch,'interrupted_unknown','not_retried_unknown_outcome')
    def status(self):
        counts=dict(self.db.execute('SELECT state,count(*) FROM batches GROUP BY state'))
        proposed=sum(len(json.loads(row[0])) for row in self.db.execute("SELECT functions FROM batches WHERE state='complete'"))
        reasons=dict(self.db.execute("SELECT error,count(*) FROM batches WHERE state='pending' AND error IS NOT NULL GROUP BY error"))
        return {'paused':self.paused(),'batches':counts,'functions_proposed_unvalidated':proposed,'functions_verified':0,'waiting':reasons}

def reserve_global(path,task,now=None,ceiling=12):
    if type(ceiling) is not int or ceiling<1: raise ValueError('invalid_request_ceiling')
    now=time.time() if now is None else now
    db=sqlite3.connect(path,timeout=30)
    try:
        db.execute('BEGIN IMMEDIATE')
        anchor=float(db.execute("SELECT value FROM meta WHERE key='anchor'").fetchone()[0])
        if now<anchor: raise RuntimeError('clock_before_anchor')
        cycle=int((now-anchor)//1800)
        count=db.execute('SELECT count(*) FROM requests WHERE cycle=?',(cycle,)).fetchone()[0]
        if count>=ceiling: db.rollback(); return None,anchor+(cycle+1)*1800
        ident='rapid-provider-'+uuid.uuid4().hex
        db.execute('INSERT INTO requests VALUES(?,?,?,?,?)',(ident,cycle,task,'rapid-provider','claimed'))
        db.commit(); return ident,anchor+(cycle+1)*1800
    finally: db.close()

def settle_global(path,ident,state):
    with closing(sqlite3.connect(path,timeout=30)) as db:
        with db:
            db.execute('UPDATE requests SET state=? WHERE id=? AND kind=?',(state,ident,'rapid-provider'))

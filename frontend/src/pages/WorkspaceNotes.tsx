import { useState } from "react";
export default function WorkspaceNotes(){ const [body,setBody]=useState(""); const [notes,setNotes]=useState<string[]>([]); return <div><h2>Workspace Notes</h2><textarea value={body} onChange={e=>setBody(e.target.value)} /><button onClick={()=>{setNotes([body,...notes]);setBody("");}}>Add</button>{notes.map((n,i)=><p key={i}>{n}</p>)}</div>; }

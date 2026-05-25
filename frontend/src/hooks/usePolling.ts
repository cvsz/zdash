import { useEffect, useRef, useState } from 'react';
export function usePolling(cb:()=>void, interval=5000){const [active,setActive]=useState(true);const r=useRef(cb);r.current=cb;useEffect(()=>{if(!active)return; const id=setInterval(()=>r.current(),interval); return ()=>clearInterval(id);},[active,interval]);return {active,pause:()=>setActive(false),resume:()=>setActive(true)};}

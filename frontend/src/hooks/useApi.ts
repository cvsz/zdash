import { useEffect, useState } from 'react';
export function useApi<T>(fn:()=>Promise<T>, deps:unknown[]=[]){const [data,setData]=useState<T|null>(null);const [loading,setLoading]=useState(true);const [error,setError]=useState<string| null>(null);useEffect(()=>{setLoading(true);fn().then(setData).catch(e=>setError(String(e))).finally(()=>setLoading(false));},deps);return {data,loading,error};}

import { mockHealth, mockLogs } from './mockData';
import { ApiError, type ApiResponse } from './types';
const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8004';
export let mockFallbackActive = false;
async function request<T>(path:string, init:RequestInit={}, fallback?:T, timeout=6000):Promise<T>{
  const controller = new AbortController(); const t = setTimeout(()=>controller.abort(), timeout);
  try { const res = await fetch(`${base}${path}`,{...init,signal:controller.signal,headers:{'Content-Type':'application/json',...(init.headers||{})}});
    const json = await res.json() as ApiResponse<T>; if(!json.ok) throw new ApiError(json.error||'API error',res.status); return json.data;
  } catch(e){ if(import.meta.env.VITE_ENABLE_MOCK_FALLBACK==='true' && fallback!==undefined){ mockFallbackActive=true; return fallback; } throw e; }
  finally { clearTimeout(t); }
}
export const apiClient = {
  get:<T>(p:string,f?:T)=>request<T>(p,{},f), post:<T>(p:string,b?:unknown,f?:T)=>request<T>(p,{method:'POST',body:JSON.stringify(b||{})},f), delete:<T>(p:string,f?:T)=>request<T>(p,{method:'DELETE'},f),
  getHealth:()=>request('/api/health',{},mockHealth), getLogs:()=>request('/api/logs',{},mockLogs)
};

export const apiGet = apiClient.get;
export const apiPostEnvelope = apiClient.post;
export const setSession = (_token?: string)=>{};

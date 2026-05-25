import { getLogs } from '../api/endpoints';import { useApi } from './useApi';export const useLogs=()=>useApi(getLogs,[]);

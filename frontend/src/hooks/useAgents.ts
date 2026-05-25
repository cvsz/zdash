import { getAgents,sendAgentMessage } from '../api/endpoints';import { useApi } from './useApi'; export const useAgents=()=>({ ...useApi(getAgents,[]), sendAgentMessage});

import { getHealth,getAgents,getRiskStatus,getSchedulerStatus,getContentStatus,getIoTStatus } from '../api/endpoints';import { useApi } from './useApi';
export const useSystemStatus=()=>useApi(async()=>({health:await getHealth(),agents:await getAgents(),risk:await getRiskStatus(),scheduler:await getSchedulerStatus(),content:await getContentStatus(),iot:await getIoTStatus()}),[]);

import type { Agent, BacktestResult, ContentItem, DrawdownResult, EventLog, HealthStatus, ScheduledJob, TradingSignal } from './types';
export const mockHealth: HealthStatus = { status: 'healthy', mock: true, services: { api: 'up', agents: 'up', risk: 'guarded' } };
export const mockAgents: Agent[] = [
  { id: 'ceo', name: 'Alexander Prime', role: 'CEO • Visionary Leader', status: 'online', health: 'ok', last_event: 'Strategic command online', capabilities: ['strategy', 'vision', 'approval'] },
  { id: 'janie', name: 'Sophia Lane', role: 'Coordinator • Manager', status: 'online', health: 'ok', last_event: 'Coordination loop active', capabilities: ['coordination', 'routing', 'management'] },
  { id: 'joe', name: 'Nathan Cole', role: 'Analyst • Developer', status: 'online', health: 'ok', last_event: 'Strategy lab ready', capabilities: ['analysis', 'development', 'backtesting'] },
  { id: 'friday', name: 'Isla Grant', role: 'Scheduler • Automation', status: 'online', health: 'ok', last_event: 'Scheduler ready', capabilities: ['scheduler', 'automation', 'dry-run'] },
  { id: 'guardian', name: 'Victor Hale', role: 'Risk Manager', status: 'online', health: 'ok', last_event: 'Guardian risk guard active', capabilities: ['risk', 'halt', 'kill-switch'] },
  { id: 'editor', name: 'Elena Voss', role: 'Content Specialist', status: 'online', health: 'ok', last_event: 'Content pipeline ready', capabilities: ['content', 'editing', 'approval'] },
  { id: 'social', name: 'Maya Quinn', role: 'Social Media Specialist', status: 'online', health: 'ok', last_event: 'Social workflow dry-run', capabilities: ['social', 'publishing', 'approval'] },
  { id: 'graphic', name: 'Julian Reed', role: 'Design Specialist', status: 'online', health: 'ok', last_event: 'Design workflow ready', capabilities: ['design', 'graphics', 'visuals'] },
];
export const mockLogs: EventLog[] = [{id:'1',category:'system',source:'mock',message:'Mock fallback mode active',ts:new Date().toISOString(),level:'warning'}];
export const mockSignals: TradingSignal[] = [{id:'s1',symbol:'XAUUSD',timeframe:'M5',side:'buy',confidence:0.71,validated:true,ai_summary:'Mock momentum bias',created_at:new Date().toISOString()}];
export const mockDrawdown: DrawdownResult = {daily:1.2,total:4.6,max_daily:5,max_total:20};
export const mockJobs: ScheduledJob[] = [{id:'j1',name:'Trading Scan',job_type:'trading_scan',cron:'*/5 * * * *',enabled:true,risk_guarded:true},{id:'j2',name:'IoT Cycle',job_type:'iot_power_cycle',cron:'0 8 * * 1',enabled:false}];
export const mockBacktests: BacktestResult[] = [{id:'b1',strategy:'ob_aggressive',metrics:{total_trades:100,win_rate:52,profit_factor:1.3,max_drawdown:12,net_profit_percent:18,consecutive_losses:4},equity_curve:[{x:'W1',y:10000},{x:'W2',y:10400}],monthly_returns:[{month:'2026-04',value:4.2}]}];
export const mockContent: ContentItem[] = [{id:'c1',title:'Gold Market Brief',status:'draft',approval_required:true,approved:false,social_dry_run:true,policy_notes:'Mock policy pending'}];

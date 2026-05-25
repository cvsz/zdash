export default function EmptyState(props:any){return <div className='card'>{props.title||props.label||props.children||'Component'}</div>}

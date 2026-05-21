export function ResultCard({result}:any){
  return <div className='card'>
    <p><b>Input:</b> {result.input_url}</p>
    <p><b>Final:</b> {result.final_url ?? 'N/A'}</p>
    <p><b>Provider:</b> {result.provider}</p>
    <button onClick={()=>navigator.clipboard.writeText(result.final_url ?? '')}>Copy</button>
    {result.final_url && <a href={result.final_url} target='_blank'>Open</a>}
  </div>
}

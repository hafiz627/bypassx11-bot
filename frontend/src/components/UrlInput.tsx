import { useState } from 'react'
export function UrlInput({onSubmit}:{onSubmit:(urls:string[])=>void}){
  const [text,setText]=useState('')
  return <div className='card'><textarea placeholder='Paste one or many URLs...' value={text} onChange={e=>setText(e.target.value)} /><button onClick={()=>onSubmit(text.split(/\s+/).filter(Boolean))}>Bypass / Resolve</button></div>
}

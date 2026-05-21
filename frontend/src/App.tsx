import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { api } from './lib/api'
import { Header } from './components/Header'
import { UrlInput } from './components/UrlInput'
import { ResultCard } from './components/ResultCard'

export default function App(){
  const [dark,setDark]=useState(true)
  const [results,setResults]=useState<any[]>([])
  useEffect(()=>{document.body.dataset.theme=dark?'dark':'light'},[dark])
  const onSubmit=async (urls:string[])=>{
    const {data}=await api.post('/api/bypass',{urls,max_depth:8,follow_redirects:true})
    setResults(data.results)
    localStorage.setItem('history', JSON.stringify(data.results))
  }
  return <main className='app'>
    <Header dark={dark} setDark={setDark}/>
    <motion.div initial={{opacity:0,y:8}} animate={{opacity:1,y:0}}>
      <UrlInput onSubmit={onSubmit} />
      <section className='grid'>{results.map((r,i)=><ResultCard key={i} result={r} />)}</section>
    </motion.div>
  </main>
}

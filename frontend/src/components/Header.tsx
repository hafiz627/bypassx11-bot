export function Header({dark, setDark}:{dark:boolean,setDark:(v:boolean)=>void}) {
  return <header className='header'><h1>Universal URL Resolver</h1><button onClick={()=>setDark(!dark)}>{dark?'Light':'Dark'} Mode</button></header>
}

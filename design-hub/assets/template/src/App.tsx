import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { DetailPage } from './pages/DetailPage'
import { HomePage } from './pages/HomePage'

export default function App() {
  return <BrowserRouter><Routes><Route path="/" element={<HomePage />} /><Route path="/:slug" element={<DetailPage />} /></Routes></BrowserRouter>
}


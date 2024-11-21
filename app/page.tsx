'use client'

import { useState, useEffect } from 'react'
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface Paper {
  title: string
  authors: string[]
  year: number
  proceedings: string
  type: string
}

export default function Home() {
  const [papers, setPapers] = useState<Paper[]>([])
  const [filteredPapers, setFilteredPapers] = useState<Paper[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [yearFilter, setYearFilter] = useState<string>('all')
  const [typeFilter, setTypeFilter] = useState<string>('all')

  useEffect(() => {
    fetch('/backdoor-papers/papers.json')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Fetched data:', data);
        setPapers(data);
        setFilteredPapers(data);
      })
      .catch(e => {
        console.error('Fetch error:', e);
      });
  }, [])

  useEffect(() => {
    const filtered = papers.filter(paper => 
      paper.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (yearFilter === 'all' || paper.year.toString() === yearFilter) &&
      (typeFilter === 'all' || paper.type === typeFilter)
    )
    setFilteredPapers(filtered)
  }, [searchTerm, yearFilter, typeFilter, papers])

  const years = Array.from(new Set(papers.map(paper => paper.year))).sort((a, b) => b - a)
  const types = Array.from(new Set(papers.map(paper => paper.type)))

  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8 text-center">Daily Machine Learning Backdoor Papers</h1>
      
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <Input
          type="text"
          placeholder="Search papers..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-grow"
        />
        <Select value={yearFilter} onValueChange={setYearFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by year" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Years</SelectItem>
            {years.map(year => (
              <SelectItem key={year} value={year.toString()}>{year}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {types.map(type => (
              <SelectItem key={type} value={type}>{type}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPapers.map((paper, index) => (
          <Card key={index}>
            <CardHeader>
              <CardTitle>{paper.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-500 mb-2">{paper.authors.join(', ')}</p>
              <p className="text-sm mb-2">Year: {paper.year}</p>
              <p className="text-sm mb-2">Proceedings: {paper.proceedings}</p>
              <p className="text-sm">Type: {paper.type}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </main>
  )
}


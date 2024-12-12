import { useState, useEffect } from 'react'
import { Input } from "./components/ui/input.tsx"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select.tsx"
import { Card, CardContent, CardHeader, CardTitle } from "./components/ui/card.tsx"

interface Paper {
  title: string
  authors: string[]
  year: number
  proceedings: string
  type: string
}

export default function PapersList() {
  const [papers, setPapers] = useState<Paper[]>([])
  const [filteredPapers, setFilteredPapers] = useState<Paper[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [yearFilter, setYearFilter] = useState<string | null>(null)
  const [proceedingsFilter, setProceedingsFilter] = useState<string | null>(null)
  const [typeFilter, setTypeFilter] = useState<string | null>(null)

  useEffect(() => {
    fetch('public/papers.json')
      .then(response => response.json())
      .then(data => {
        setPapers(data)
        setFilteredPapers(data)
      })
      .catch(error => console.error('Error fetching papers:', error))
  }, [])

  useEffect(() => {
    const filtered = papers.filter(paper => 
      paper.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (yearFilter === null || paper.year.toString() === yearFilter) &&
      (proceedingsFilter === null || paper.proceedings === proceedingsFilter) &&
      (typeFilter === null || paper.type === typeFilter)
    )
    setFilteredPapers(filtered)
  }, [searchTerm, yearFilter, proceedingsFilter, typeFilter, papers])

  const uniqueYears = Array.from(new Set(papers.map(paper => paper.year))).sort((a, b) => b - a)
  const uniqueProceedings = Array.from(new Set(papers.map(paper => paper.proceedings)))
  const uniqueTypes = Array.from(new Set(papers.map(paper => paper.type)))

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8 text-center">Daily Papers</h1>
      
      <div className="mb-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Input
          placeholder="Search papers..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full"
        />
        <Select value={yearFilter} onValueChange={setYearFilter}>
          <SelectTrigger>
            <SelectValue placeholder="Filter by Year" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Years</SelectItem>
            {uniqueYears.map(year => (
              <SelectItem key={year} value={year.toString()}>{year}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={proceedingsFilter} onValueChange={setProceedingsFilter}>
          <SelectTrigger>
            <SelectValue placeholder="Filter by Proceedings" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Proceedings</SelectItem>
            {uniqueProceedings.map(proc => (
              <SelectItem key={proc} value={proc}>{proc}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger>
            <SelectValue placeholder="Filter by Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {uniqueTypes.map(type => (
              <SelectItem key={type} value={type}>{type}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredPapers.map((paper, index) => (
          <Card key={index}>
            <CardHeader>
              <CardTitle>{paper.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-2">
                {paper.authors.join(', ')}
              </p>
              <div className="flex justify-between text-sm">
                <span>{paper.year}</span>
                <span>{paper.proceedings}</span>
                <span>{paper.type}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}


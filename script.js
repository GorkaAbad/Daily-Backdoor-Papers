async function loadPapers() {
    const response = await fetch('papers.json');
    const papers = await response.json();
    const container = document.getElementById('papers-container');
    container.innerHTML = '';
    papers.forEach(paper => {
        const paperDiv = document.createElement('div');
        paperDiv.classList.add('paper');
        paperDiv.innerHTML = `
            <h2>${paper.title}</h2>
            <p>${paper.proceedings}</p>
            <p>Authors: ${paper.authors.join(', ')}</p>
            <p>Published on: ${new Date(paper.year).toLocaleDateString()}</p>
        `;
        container.appendChild(paperDiv);
    });
}

loadPapers();


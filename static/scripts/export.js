async function exportAsHtml() {
  const html = await window.editorjsInterop.exportHtml();
  const blob = new Blob([html], { type: 'text/html' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'note.html';
  a.click();
}

async function exportAsMarkdown() {
  const markdown = await window.editorjsInterop.exportMarkdown();
  const blob = new Blob([markdown], { type: 'text/markdown' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'note.md';
  a.click();
}

async function exportAsPdf() {
  const container = document.getElementById("editor");
  await html2pdf()
    .set({
      margin: 0.5,
      filename: 'note.pdf',
      html2canvas: { scale: 1, useCORS: true },
      jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' },
      pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
    })
    .from(container)
    .toPdf()
    .get('pdf')
    .then(pdf => {
      pdf.internal.write(0, 'BT /F1 12 Tf ET');
    })
    .save();
}

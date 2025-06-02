﻿window.editorjsInterop = {
    instance: null,
    parser: null,
    exportMarkdown: exportMarkdown,

    init: function (savedData) {

        window.note_id = window.location.pathname.replace("/", "");
        
        const config = {
            image: { use: 'img', class: 'editor-image' },
            paragraph: { class: 'editor-paragraph' },
            header: { class: 'editor-header' },
            list: { class: 'editor-list' },
            table: { class: 'editor-table' },
            code: { class: 'editor-code' }
        };
        

        const customParsers = {
            delimiter: () => '<hr/>',
            toggle: (data) =>
                `<details><summary>${data.title}</summary><div>${data.message}</div></details>`
        };

        const embedMarkup = (embedData) => {
            if (embedData.service === 'youtube') {
                const videoId = embedData.source.split('v=')[1];
                return `<iframe width="100%" height="315" src="https://www.youtube.com/embed/${videoId}" frameborder="0" allowfullscreen></iframe>`;
            }
            return '';
        };

        this.parser = new edjsParser(config, customParsers, embedMarkup);

        this.instance = new EditorJS({
            holder: 'editor',
            placeholder: 'Start typing your note...',
            tools: {
                image: {
                    class: window.SimpleImage,
                    toolbox: window.SimpleImage.toolbox
                },
                header: {
                    class: window.Header,
                    inlineToolbar: true,
                    config: {
                        placeholder: 'Enter a heading',
                        levels: [1, 2, 3, 4],
                        defaultLevel: 2
                    }
                },
                delimiter: {
                    class: window.Delimiter,
                    config: {
                        defaultStyle: 'line',
                        defaultLineWidth: 100,
                        defaultLineThickness: 3
                    }
                },
                toggle: {
                    class: window.ToggleBlock,
                    inlineToolbar: true,
                    config: {
                        titlePlaceholder: 'Toggle title',
                        messagePlaceholder: 'Toggle content'
                    }
                },
                paragraph: {
                    class: Paragraph,
                    inlineToolbar: true
                },
                list: {
                    class: EditorjsList,
                    inlineToolbar: true,
                    config: {
                        defaultStyle: 'unordered'
                    }
                },
                linkTool: {
                    class: LinkTool,
                    config: {
                        endpoint: window.location.origin + '/api/fetchUrl'
                    }
                },
                mermaid: MermaidTool,
                table: Table,
                inlineCode: {
                    class: InlineCode,
                    shortcut: 'CMD+SHIFT+M'
                },
                underline: Underline,
                style: EditorJSStyle.StyleInlineTool,
                Color: {
                    class: ColorPlugin,
                    config: {
                        colorCollections: ['#EC7878', '#9C27B0', '#673AB7', '#3F51B5', '#0070FF', '#03A9F4', '#00BCD4', '#4CAF50', '#8BC34A', '#CDDC39', '#FFF'],
                        defaultColor: '#FF1300',
                        type: 'text',
                        customPicker: true
                    }
                },
                Marker: {
                    class: ColorPlugin,
                    config: {
                        defaultColor: '#FFBF00',
                        type: 'marker',
                        icon: `<svg fill="#000000" height="200px" width="200px" ...>...</svg>`
                    }
                }
            },
            data: savedData ? JSON.parse(savedData) : {},
            
            autofocus: true,
            onReady: () => {
                console.log("Editor.js is ready!");
                MermaidTool.config({ 'theme': 'neutral' });
                new Undo({ editor: this.instance }); // <-- pass the actual editor instance

                document.getElementById("export-container").style.display = "block";

                // Wait a tick to ensure all blocks are rendered
                setTimeout(async () => {
                    const count = this.instance.blocks.getBlocksCount();

                    if (count > 0) {
                        const lastBlock = this.instance.blocks.getBlockByIndex(count - 1);

                        if (lastBlock && lastBlock.holder && lastBlock.holder.innerText.trim() !== "") {
                            this.instance.caret.setToBlock(count - 1, "end");
                        }
                    }
                }, 0);
            },
            onChange: (api, event) => {
                console.log("Editor content changed", event);
                startAutoSaveTimer(); // triggers save on content change
            }
        });
    },

    getContent: async function () {
        if (!this.instance) return "";
        try {
            const output = await this.instance.save();
            return JSON.stringify(output);
        } catch (err) {
            console.error("Editor.js save failed:", err);
            return "";
        }
    },

    setContent: async function (json) {
        if (!this.instance || !json) return;
        try {
            const data = JSON.parse(json);
            await this.instance.render(data);
        } catch (err) {
            console.error("Editor.js render failed:", err);
        }
    },

    exportHtml: async function () {
    if (!this.instance) return "";

    try {
        const output = await this.instance.save();

        const htmlParts = output.blocks.map(block => {
            const { type, data } = block;

            switch (type) {
                case "header":
                    return `<h${data.level}>${data.text}</h${data.level}>`;

                case "paragraph":
                    return `<p>${data.text}</p>`;

                case "list":
                    const tag = data.style === "ordered" ? "ol" : "ul";
                    return `<${tag}>${
                        data.items.map(item =>
                            `<li>${item.content || item}</li>`
                        ).join("")
                    }</${tag}>`;

                case "delimiter":
                    return `<hr style="border-top:${data.lineThickness || 1}px solid #ccc;width:${data.lineWidth || 100}%" />`;

                case "image":
                    return `<img src="${data.url}" alt="" style="max-width:100%;display:block;margin:1rem auto;" />`;

                case "toggle":
                    return `<details><summary>${data.title}</summary><div>${data.message}</div></details>`;

                case "table":
                    return `<table><tbody>${
                        data.content.map(row =>
                            `<tr>${row.map(cell => `<td>${cell}</td>`).join("")}</tr>`
                        ).join("")
                    }</tbody></table>`;

                default:
                    return `<div>[Unhandled block type: ${type}]</div>`;
            }
        });

        return htmlParts.join("\n");
    } catch (err) {
        console.error("Editor.js export failed:", err);
        return "";
    }
}

};

async function exportMarkdown() {
if (!window.editorjsInterop?.instance) return "";

try {
const output = await window.editorjsInterop.instance.save();

const mdParts = output.blocks.map(block => {
    const { type, data } = block;

    switch (type) {
    case "header":
        return `${"#".repeat(data.level)} ${data.text}`;
    case "paragraph":
        return data.text;
    case "list":
        return data.items.map(item => {
        const content = convertInlineHTML(item.content || item);
        return data.style === "ordered" ? `1. ${content}` : `- ${content}`;
        }).join("\n");
    case "delimiter":
        return `---`;
    case "image":
        return `![Image](${data.url})`;
    case "toggle":
        return `**${data.title}**\n\n${data.message}`;
    case "table":
        const rows = data.content;
        if (!rows.length) return "";
        const header = rows[0].map(() => "---").join(" | ");
        const table = rows.map(r => r.join(" | ")).join("\n");
        return `${rows[0].join(" | ")}\n${header}\n${table.split("\n").slice(1).join("\n")}`;
    default:
        return `<!-- Unhandled block: ${type} -->`;
    }
});

return mdParts.join("\n\n");
} catch (err) {
console.error("Markdown export failed:", err);
return "";
}
}
// MD helper to convert inline html to MD
function convertInlineHTML(text) {
return text
.replace(/<b>(.*?)<\/b>/gi, '**$1**')
.replace(/<i>(.*?)<\/i>/gi, '*$1*')
.replace(/<u>(.*?)<\/u>/gi, '__$1__')
.replace(/<br\s*\/?>/gi, '\n');
}


// async function exportToPdf() {
// const container = document.getElementById("editor");

// await html2pdf()
// .set({
//     margin: 0.5,
//     filename: 'note.pdf',
//     html2canvas: { scale: 1, useCORS: true },
//     jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' },
//     pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
// })
// .from(container)
// .toPdf()
// .get('pdf')
// .then(pdf => {
//     // (optional) inject font layer
//     pdf.internal.write(0, 'BT /F1 12 Tf ET');
// })
// .save();
// }







// Delay to simulate "OnAfterRenderAsync"
// window.addEventListener("DOMContentLoaded", function () {
    
//     setTimeout(function () {
//         try {
//             window.editorjsInterop.init(savedJson);
//         } catch (err) {
//             console.error("?? JSInterop failed:", err);
//         }
//     }, 0); // Delay for stability
// });
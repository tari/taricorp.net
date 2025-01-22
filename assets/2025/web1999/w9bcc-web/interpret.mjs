import w99bcc from './w99bcc.js'

const IE16_ICON_B64 = `
iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAClUlEQVQ4y42TT0jTARTHP785U8hZ
Lokc2mHVjFAiD0HBCIRC6hBCHYOS2KFTt1hFEUQJIZGNDguE2SEiISwkCC0zilqRVBMlNVHzH3Nb
/bZJufn7drCmZocefA8P3vvwvrz3DEniP2JyEnp74wwPz5LJZPF4SqmtdWL8CxCPZxgYyKe/fzGP
RsHvn6Gra5ra2p0AJJNpHj6cBS2LROK7mpo65fFYyiuWNlZ/E3kSSLAgtzumUGhIppmUJPn9H8Xy
Zp/vjkA6eOKpzl4/p9JtY8L2B7Akn29ciYSpSGRmEWCaafl8QbH2sZrbLqmj84wqNqUEktc7IBhc
BWls7JOkRUB7+2sVFV3Wo56Tev3mtNY70vJ6fygcHtfc3JzC4bC83pYVALd7WslkSmSzlny+m3rw
4JDehY+ouDgukAKBXlmWpUwmI8uyFAgEBdYKyOfPU7IbhoHL1cOuXTH27WvCNEsACAZddHSMY1k2
bDaYmNgPGCu2FYmkIBabUvezAzp69PZfPn8IMsv0UzAriObU2vpW9i9Dz+l6v4X7bSeBl8AOoISr
V19QX7+ZhQULwzDIz7djmt+xrKUJyspc2HteXaD1biOI3wAnUEI8vp3KyvJc8eDgCKHQOubn1wFi
fl5cuVKA/etsgrGPh4G7QAqYBLZz7Vo56fQgNTU/iUaz+P2lwBKwvn4Up7MEjjfUqbxcamm5J7f7
lOCW4IMgu2r3SzLV1zexeAc3moNyu8ckSf39A2pouCg4L2gXxFY1Hzs2qkjka+78jU99w6rek09s
xIXTmUcymSIQuEdn5xsKCkqBtRQWVlBXt5eqqjVUVztxOIpyVgxJevJkiFCom5oaBxs2ONi928PW
rZux2Wy5Qrvd/s83/wWkm9GVjZptygAAAABJRU5ErkJggg==
`

const IE16_ICON_ALPHA_B64 = `
iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QAMQBlAK2DefzXAAAA00lE
QVQ4y5VT2w0DIQxzqm4UZspOZqYwk/tx3IuDqo3kk9DhxHGC4a9I3c/F7DtBA2G8n3o9SdRGlNxn
CUcVE7JHiqQceSS7Y5qEAigylMnhci6TGAA4qIaGzG5N4aRnCggsPAmRrsw4+3/I9ImKnR6uTMg9
JzLXbRxFMl0RXBj2DRRIiIyhYv/5Q7wAoNZ94K1js3a+iYMHEbhUjGH2Ke9YjfF9Vmr9e1Xgx+kZ
xXoL3snVNjQAtWMW7bYfdvZWLksT4w50lMfjs3PLcDGw2q8P/AOOnuCKsl0/HwAAAABJRU5ErkJg
gg==
`

class Interpreter {
    #FILES_KEY_NAME = "interpreterFiles"

    #files

    constructor() {
        this.#files = new Map()

        let files = localStorage.getItem(this.#FILES_KEY_NAME)
        if (files !== null) {
            files = JSON.parse(files)
        } else {
            files = {
                'icon.png': IE16_ICON_B64,
                'icon-transparent.png': IE16_ICON_ALPHA_B64,
            }
        }
        for (const [k, v] of Object.entries(files)) {
            this.#files.set(k, Uint8Array.from(atob(v), c => c.charCodeAt(0)))
        }
    }

    save() {
        const out = {}
        for (const [name, fileData] of this.#files.entries()) {
            const dataStr = fileData.reduce((data, byte) => data + String.fromCharCode(byte), '')
            out[name] = btoa(dataStr)
        }

        localStorage.setItem(this.#FILES_KEY_NAME, JSON.stringify(out))
    }

    async addFile(f) {
        const data = await f.arrayBuffer()
        this.#files.set(f.name, new Uint8Array(data))
    }

    *getFiles() {
        for (const [name, data] of this.#files.entries()) {
            yield [name, data]
        }
    }

    async evaluate(text) {
        let messages = []

        const module = await w99bcc({
            // See INCOMING_MODULE_JS_API
            print: (x) => messages.push(x),
            printErr: (x) => messages.push(x),
            noInitialRun: true,
        })

        module.FS.mkdir('/resources')
        for (const [name, data] of this.getFiles()) {
            module.FS.writeFile('/resources/' + name, data)
        }

        module.FS.writeFile('/in.lua', text, { encoding: 'utf8' });
        module.FS.chdir('/resources')
        const result = module.callMain(['/in.lua', '/out.bin', '--print-stats'])
        if (result !== 0) {
            throw new Interpreter.Error(result, messages)
        }
        return {
            bytecode: module.FS.readFile('/out.bin', { encoding: 'binary' }),
            messages: messages,
        }
    }

    static Error = class BccError extends Error {
        constructor(code, messages) {
            super("Bytecode compiler returned an error")
            this.code = code
            this.messages = messages
        }
    }
}

export default Interpreter

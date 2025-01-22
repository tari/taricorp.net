import w99bci from './w99bci.mjs'

class Renderer {
    #canvas
    #module
    #paletteRGB
    #fontBitmaps

    static async create(canvas) {
        // Let module loading begin while we're getting the palette.
        const module = w99bci({
            // See INCOMING_MODULE_JS_API
            print: (x) => console.log('Renderer:', x),
            printErr: (x) => console.warn('Renderer:', x),
        })

        return new Renderer(canvas, await module, await this.#loadPaletteRGB(), await this.#loadFontBitmap())
    }

    render(data) {
        const width = data[0] | (data[1] << 8)
        const height = data[2]
        let title = ''
        let i = 3
        while (i < data.length) {
            if (data[i] === 0) {
                i += 1
                break
            }
            title += String.fromCharCode(data[i])
            i += 1
        }

        this.#canvas.width = width
        this.#canvas.height = height

        const renderer = new this.#module.Renderer(this.#canvas, this.#paletteRGB, this.#fontBitmaps)
        renderer.render(data.slice(i))
    }

    constructor(canvas, module, paletteRGB, fontBitmaps) {
        this.#canvas = canvas
        this.#module = module
        this.#paletteRGB = paletteRGB
        this.#fontBitmaps = fontBitmaps
    }

    static async #loadPaletteRGB() {
        const image = await new Promise((resolve, reject) => {
            const paletteImage = new Image()
            paletteImage.onload = () => {
                resolve(paletteImage)
            }
            paletteImage.onerror = () => {
                reject()
            }
            paletteImage.src = 'palette_system_winvga_web216.png'
        });

        const canvas = document.createElement('canvas')
        canvas.width = image.width
        canvas.height = image.height

        const ctx = canvas.getContext('2d')
        ctx.drawImage(image, 0, 0)
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)

        const rgbArray = []
        for (let i = 0; i < imageData.width * imageData.height * 4; i += 4) {
            const r = imageData.data[i]
            const g = imageData.data[i + 1]
            const b = imageData.data[i + 2]
            rgbArray.push([r, g, b])
        }

        return rgbArray
    }

    static async #loadFontBitmap() {
        const image = await new Promise((resolve, reject) => {
            const paletteImage = new Image()
            paletteImage.onload = () => {
                resolve(paletteImage)
            }
            paletteImage.onerror = () => {
                reject()
            }
            paletteImage.src = 'Font2.png'
        });

        const canvas = document.createElement('canvas')
        canvas.width = image.width
        canvas.height = image.height
        const ctx = canvas.getContext('2d')
        ctx.drawImage(image, 0, 0)

        const chars = []
        for (let i = 0; i < 256; i++) {
            const x = i % 16
            const y = Math.floor(i / 16)

            // Get data for this glyph
            const imageData = ctx.getImageData(12 * x + 2, 12 * y + 3, 12, 12)

            // Find the glyph's width, in pixels
            let width = 0
            let cx = imageData.width;
            let stop = false
            while (!stop && cx >= 0) {
                cx -= 1
                for (let cy = 0; cy < imageData.height; cy += 1) {
                    const v = imageData.data[(cy * 4 * imageData.width) + (cx * 4)]
                    if (v === 0) {
                        stop = true
                        break
                    }
                }
            }
            if (cx >= 0) {
                // Found a pixel that's dark at column cx
                width = cx + 1
            }

            // Generate a list of character row data, top to bottom
            const charData = []
            for (let cy = 0; cy < imageData.height; cy++) {
                const dataRow = []
                for (let cx = 0; cx < width; cx++) {
                    dataRow.push(imageData.data[(cy * 4 * imageData.width) + (cx * 4)] === 0)
                }
                charData.push(dataRow)
            }
            chars.push(charData)
        }

        return chars
    }
}

export default Renderer

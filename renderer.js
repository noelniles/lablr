const fs = require('fs')
const path = require('path')
let files = []


function shuffle(a) {
    // Shuffle an array. This is used to get random training examples.
    var j, x, i

    for (i = a.length - 1; i > 0; i--) {
        j = Math.floor(Math.random() * (i+1))
        x = a[i]
        a[i] = a[j]
        a[j] = x
    }
    return a
}

function draw(e) {
    if (!isdrawing) return

}

function workspace() {
    return {
        isdrawing: false,
        current_image: new Image(),
        files: this.produce_files,
        canvas: document.getElementById('workspace'),
        context: this.canvas.getContext("2d"),

        init: function() {
            canvas.addEventListener('mousedown', () => isdrawing = true)
            canvas.addEventListener('mousemove', draw)
            canvas.addEventListener('mouseup', () => isdrawing = false)
            canvas.addEventListener('mouseout', () => isdrawing = false)
        },

        produce_files: function* () {
            // Construct the path to the data.
            const folder = path.join('./pibeach-0004')

            files = []
            fs.readdirSync(folder).forEach(file =>{
                fullpath = path.join(folder, file)
                files.push(fullpath)
            })
            files = shuffle(files)
            console.log('files: ', files)

            for (let f of files) {
                console.log(f)
                yield f
            }
        },

        draw: function() {
            console.log('Drawing..............')
            this.context.drawImage(this.current_image, 0, 0,
                this.canvas.width, this.canvas.height)
            this.current_image.src = files.next().value
        }

    }
}
window.onload = function() {
    let ws = workspace()
    ws.init()
    ws.draw()

    //// Initialize the canvas.
    //init(canvas)
    //// Connect all the listeners.
    //img = new Image()
    //let gen = produce_files()

    //img.onload = function() {
    //    context.drawImage(img, 0, 0, canvas.width, canvas.height)
    //}
    //img.src = gen.next().value

    //document.getElementById('next-btn').onclick = function() {
    //   img.src = gen.next().value
    //}
}
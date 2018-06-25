const fs = require('fs')
const path = require('path')


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

function produce_files() {
    // Construct the path to the data.
    const folder = path.join('./data/pibeach-0003')

    files = []
    fs.readdirSync(folder).forEach(file =>{
        fullpath = path.join(folder, file)
        files.push(fullpath)
    })
    files = shuffle(files)
    return files
}

class workspace {
    constructor(canvas, context, files) {
        let self = this // This is so we can use this inside the onload function.
        this.canvas = canvas
        this.context = context
        this.isdrawing = false
        this.files = files
        this.current_index = 0
        this.previous_index = 0

        this.canvas.addEventListener('mousedown', () => this.isdrawing = true)
        this.canvas.addEventListener('mousemove', this.draw)
        this.canvas.addEventListener('mouseup', () => this.isdrawing = false)
        this.canvas.addEventListener('mouseout', () => this.isdrawing = false)

        this.current_image = new Image()
        this.current_image.onload = function () {
            self.load_image(self.current_index)
        }
        console.log('First file: ', this.files[this.current_index])
        this.current_image.src = this.files[this.current_index]
    }

    load_image(i) {
        this.previous_index = this.current_index
        this.current_index = i
        this.context.drawImage(this.current_image, 0, 0, this.canvas.width, this.canvas.height)
    }

    draw() {
        this.isdrawing = true
    }

    next() {
        let next_index = this.current_index + 1
        this.load_image(next_index)
    }

}

window.onload = function() {
    let canvas = document.getElementById('workspace')
    let context = canvas.getContext("2d")
    let next_button = document.getElementById('next-btn')
    let files = produce_files()

    let ws = new workspace(canvas, context, files)
    next_button.addEventListener('click', ws.next)

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
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

function produce_files(directory) {
    if (directory === '') {
        return
    }
    // Construct the path to the data.
    const folder = path.join(directory)

    files = []
    fs.readdirSync(folder).forEach(file =>{
        fullpath = path.join(folder, file)
        files.push(fullpath)
    })
    files = shuffle(files)
    return files
}

class workspace {
    constructor(canvas, context) {
        let self = this // This is so we can use this inside the onload function.
        this.data_directory = ''
        this.canvas = canvas
        this.context = context
        this.isdrawing = false
        this.files = []
        this.current_index = 0
        this.previous_index = 0

        this.canvas.addEventListener('mousedown', () => this.isdrawing = true)
        this.canvas.addEventListener('mousemove', this.draw)
        this.canvas.addEventListener('mouseup', () => this.isdrawing = false)
        this.canvas.addEventListener('mouseout', () => this.isdrawing = false)

        this.current_image = new Image()

        this.current_image.onload = function () {
            self.context.drawImage(self.current_image, 0, 0, self.canvas.width, self.canvas.height)
        }
    }

    add_files(files) {
        // Add a list of files to the workspace.
        this.files.push(...files)
    }

    load_image(i) {
        this.previous_index = this.current_index
        this.current_index = i
        let filename = this.files[this.current_index]
        this.current_image.src = filename
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
    let go_button = document.getElementById('go')
    let url_box = document.getElementById('img-url')

    // Make a workstation.
    let ws = new workspace(canvas, context)

    // Connect the buttons.
    let next_button = document.getElementById('next-btn')
    next_button.addEventListener('click', ws.next)

    go_button.addEventListener('click', function() {
        let directory = url_box.value
        let files = produce_files(directory)
        ws.add_files(files)
        ws.next()
    })
}
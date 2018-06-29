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
        this.lastX = 0
        this.lasty = 0
        this.last_width = 0
        this.last_height = 0
        this.mousepressed = false
        this.points = []
        this.operating_mode = 'draw'

        this.canvas.addEventListener('mousedown', () => this.mousepressed = true)
        this.canvas.addEventListener('mousemove', function(e) {
            // Right click means we're marking background pixels
            let drawing_background = e.button === 2
            if (self.mousepressed) {
                let posX = e.pageX - this.offsetLeft
                let posY = e.pageY - this.offsetTop
                self.draw(posX, posY, true)
            }
        })
        this.canvas.addEventListener('mouseup', () => this.mousepressed = false)
        this.canvas.addEventListener('mouseout', () => this.mousepressed = false)

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

    draw(x, y, isdown) {
        if (this.operating_mode === 'draw') {
            if (isdown) {
                this.context.beginPath()
                this.context.strokeStyle = 'red'
                this.context.lineJoin = 'round'
                this.context.moveTo(this.lastX, this.lastY)
                this.context.lineTo(x, y)
                this.points.push([x, y])
                this.context.closePath()
                this.context.stroke()
            }
            this.lastX = x
            this.lastY = y
        }
        else if (this.operating_mode == 'crop') {
            console.log('cropping stuff')
            let mousex = x
            let mousey = y
            let width = mousex - this.lastX
            let height = mousey - this.lastY
            this.last_width = width
            this.last_height = height
            this.context.beginPath()
            this.context.strokeStyle = 'red'
            this.context.lineJoin = 'round'
            this.context.rect(this.lastX, this.lastY, width, height)
            this.context.stroke()
        }
    }

    next() {
        let next_index = this.current_index + 1
        this.load_image(next_index)
    }

    save() {
        console.log('saving')
        console.log('points: ', this.points)
    }
}

window.onload = function() {
    let hasfiles = false
    let canvas = document.getElementById('workspace')
    let context = canvas.getContext("2d")
    let go_button = document.getElementById('go')
    let url_box = document.getElementById('img-url')
    let points = []

    // Make a workstation.
    let ws = new workspace(canvas, context)

    // Connect the buttons.
    let next_button = document.getElementById('next-btn')
    next_button.addEventListener('click', function() {
        if (!hasfiles) {
            console.log('no files')
            return
        }
        ws.next()
    })

    save_button = document.getElementById('save-btn')
    save_button.addEventListener('click', function() {
        ws.save()
    })

    go_button.addEventListener('click', function() {
        let directory = url_box.value
        let files = produce_files(directory)
        ws.add_files(files)
        hasfiles = true
        ws.next()
    })

    crop_button = document.getElementById('crop-btn')
    crop_button.addEventListener('click', function(e) {
        ws.operating_mode = 'crop'
    })
}
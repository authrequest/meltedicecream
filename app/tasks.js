const Task = require('./task');
const { EventEmitter } = require('events');
const { ipcMain } = require('electron');
const store = require('./store');

global.tasks = [];

class Tasks extends EventEmitter {

    constructor() {
        super()

        this.create = this.create.bind(this);
        this.remove = this.remove.bind(this);
        this.removeAll = this.removeAll.bind(this);
        this.list = this.list.bind(this);
        this.get = this.get.bind(this);
        this.startAll = this.startAll.bind(this);
        this.start = this.start.bind(this);
        this.stop = this.stop.bind(this);
        this.stopAll = this.stopAll.bind(this);
        this.sendIt = this.sendIt.bind(this)

        this.lastTask = null;
        ipcMain.on('captcha', this.sendIt)

    }

    sendIt(cap) {
        for(let i=0; i<global.tasks.length; i++) {
            var task = global.tasks[i];
            if(task.waitingOnCap) {
                console.log("1 is waiting")
                return task.emit('cap', cap);
            }
        }
    }

    create(config, profile) {
        
        const secret = store.get('hwid', 'licensing');
        let task = new Task(config, secret);
        task.profilename = profile;
        
        let lastEl = global.tasks[global.tasks.length - 1];
        let id;
        if(lastEl)
            id = lastEl.id + 1;
        else
            id = global.tasks.length;

        task.id = id;
        global.tasks.push(task);
        
        task.on('progress', () => this.emit('update'))
        task.on('error', () => this.emit('update'))

        this.emit('update');
        return task;
    }

    remove(id) {

        global.tasks = global.tasks.filter(Boolean);
        let task = global.tasks.find(i => i.id == id);
        let index = global.tasks.indexOf(task);
        if(!task) throw new Error('Task does not exist');
        
        task.stop();
        task.removeAllListeners();
        delete global.tasks[index];
        global.tasks = global.tasks.filter(Boolean);
        this.emit('update');
        return true;

    }

    removeAll() {
        global.tasks = global.tasks.filter(Boolean);
        let work = global.tasks.map(i => new Promise(
            resolve => {
                this.remove(i.id); resolve();
            }
        ));
        Promise.all(work);
    }

    list() {
        return global.tasks;
    }

    get(id) {
        return global.tasks.find(i => i.id == id);
    }

    startAll() {
        global.tasks = global.tasks.filter(Boolean);
        for(let i=0; i<global.tasks.length; i++) {
            let task = global.tasks[i];
            if(!task) continue;
            task.start();
            this.emit('update')
        }
    }

    start(id) {
        let task = global.tasks.find(i => i.id == id);
        if(!task) throw new Error('Task does not exist');
        task.start();
        this.emit('update')
    }

    stop(id) {
        let task = global.tasks.find(i => i.id == id);
        if(!task) throw new Error('Task does not exist');
        task.stop();
        this.emit('update')
    }

    stopAll() {
        global.tasks = global.tasks.filter(Boolean);
        for(let i=0; i<global.tasks.length; i++) {
            let task = global.tasks[i];
            if(!task) continue;
            task.stop();
            this.emit('update')
        }
    }

}

module.exports = Tasks;
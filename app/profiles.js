const store = require('./store');
const { EventEmitter } = require('events');

class Profiles extends EventEmitter {

    constructor() {
        super()

        this.list = this.list.bind(this);
        this.get = this.get.bind(this);
        this.create = this.create.bind(this);
        this.delete = this.delete.bind(this);
        this.deleteAll = this.deleteAll.bind(this);
    }

    list() {
        return store.get(null, 'profiles') || [];
    }

    get(name) {
        return store.get(name, 'profiles');
    }

    create(name, profile) {
        store.set(name, profile, 'profiles');
        this.emit('create', name);
        return true;
    }

    delete(name) {
        store.delete(name, 'profiles');
        this.emit('remove', name);
    }

    deleteAll() {
        console.log("It wotrk")
        try {

            store.delete(null, 'profiles');
            this.emit('remove');
        } catch (e) {
            console.log(e)

        }
    }

}

module.exports = Profiles;
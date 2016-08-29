function tick() {
    // get the mins of the current time
    var mins = new Date().getMinutes();
    if (mins == '5') {
        // reload the page to get new data
        location.reload();
    } else {
        console.log('Tick ' + mins);
    }
}

setInterval(tick, 1000 * 31);

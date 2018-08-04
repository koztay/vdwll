// target elements with the "draggable" class

interact('.resize-drag')
    .draggable({
        onmove: window.dragMoveListener,
        restrict: {
            restriction: 'parent',
            elementRect: {top: 0, left: 0, bottom: 1, right: 1}
        },
    })
    .resizable({
        // resize from all edges and corners
        edges: {left: true, right: true, bottom: true, top: true},

        // keep the edges inside the parent
        restrictEdges: {
            outer: 'parent',
            endOnly: true,
        },

        // minimum size
        restrictSize: {
            min: {width: 100, height: 50},
        },

        inertia: true,
    })
    .on('resizemove', function (event) {
        var target = event.target,
            x = (parseFloat(target.getAttribute('data-x')) || 0),
            y = (parseFloat(target.getAttribute('data-y')) || 0);

        // update the element's style
        target.style.width = event.rect.width + 'px';
        target.style.height = event.rect.height + 'px';

        // translate when resizing from top or left edges
        x += event.deltaRect.left;
        y += event.deltaRect.top;

        target.style.webkitTransform = target.style.transform =
            'translate(' + x + 'px,' + y + 'px)';

        target.setAttribute('data-x', x);
        target.setAttribute('data-y', y);
        target.textContent = Math.round(event.rect.width) + '\u00D7' + Math.round(event.rect.height);
    })
    .on('doubletap', function (event) {
        console.log("double tap çalıştı");
        if ($(event.target).parent('div#outer-dropzone').length) {
        console.log("ben zone 'dayım");
        document.getElementById("main-container").appendChild(event.target);
        document.getElementById("outer-dropzone").removeChild(event.target);
    }
        event.preventDefault();
  });

/* The dragging code for '.draggable' from the demo above
 * applies to this demo as well so it doesn't have to be repeated. */

// enable draggables to be dropped into this
interact('.dropzone').dropzone({
    // only accept elements matching this CSS selector
    accept: '#yes-drop',
    // Require a 75% element overlap for a drop to be possible
    overlap: 0.75,

    // listen for drop related events:
    ondropactivate: function (event) {
        // add active dropzone feedback
        event.target.classList.add('drop-active');
    },
    ondragenter: function (event) {
        var draggableElement = event.relatedTarget,
            dropzoneElement = event.target;
        // feedback the possibility of a drop
        dropzoneElement.classList.add('drop-target');
        draggableElement.classList.add('can-drop');
        draggableElement.textContent = 'Dragged in';
    },
    ondragleave: function (event) {
        // remove the drop feedback style
        event.target.classList.remove('drop-target');
        event.relatedTarget.classList.remove('can-drop');
        event.relatedTarget.textContent = 'Dragged out';

    },
    ondrop: function (event) {
        var x = event.relatedTarget.getAttribute('data-x');
        var y = event.relatedTarget.getAttribute('data-y');
        event.relatedTarget.textContent = 'Dropped :' + " x :" + x + " y :" + y;
        console.log("parent node:", event.relatedTarget.parentElement);
        // $(event.relatedTarget).prop("id", "newId").appendTo("#outer-dropzone");
        document.getElementById("outer-dropzone").appendChild(event.relatedTarget);
        // event.relatedTarget.innerHTML = '<a href="#" ' +
        //     'id="remove" ' +
        //     'onclick="remove_element(event.relatedTarget)">Remove</a>';


    },
    ondropdeactivate: function (event) {
        // remove active dropzone feedback
        event.target.classList.remove('drop-active');
        event.target.classList.remove('drop-target');
    }
});

function remove_element(element) {
    var elem = $(element);
    document.getElementById("outer-dropzone").removeChild(elem);
}

function dragMoveListener(event) {
    console.log("dragMoveListener çalıştı");
    var target = event.target,
        // keep the dragged position in the data-x/data-y attributes
        x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx,
        y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

    // translate the element
    target.style.webkitTransform =
        target.style.transform =
            'translate(' + x + 'px, ' + y + 'px)';

    // update the posiion attributes
    target.setAttribute('data-x', x);
    target.setAttribute('data-y', y);
    target.textContent = 'dragged :' + " x :" + x + " y :" + y;

    interact(target).draggable({
        snap: {
            targets: [
                {x: 0, y: 0},                                       // anchor
                interact.createSnapGrid({x: 25, y: 25}),            // grid
                function (x, y) {
                    return {x: x % 50, y: y % 50};
                }  // path function
            ],
            relativePoints: [{x: 0.5, y: 0.5}]                  // instead of elementOrigin
            // other snap settings...
        }
    });
    // Aşağıdaki kod çalışmıyor...
    if ($(target).parent('div#outer-dropzone').length) {
        console.log("ben zone 'dayım");
        // document.getElementById("main-container").appendChild(target);
        // document.getElementById("outer-dropzone").removeChild(target);
    }
}

//
// function resizeMoveListener(event)
// {
//     console.log("resizeMoveListener çalıştı");
//     //get scale of drop container
//     //see http://stackoverflow.com/questions/5603615/get-the-scale-value-of-an-element
//     var container = $('#pagecontainers')[0];
//     var scaleX = container.getBoundingClientRect().width / container.offsetWidth;
//     var scaleY = container.getBoundingClientRect().height / container.offsetHeight;
//
//     //apply transform
//     var target = event.target;
//     var x = event.rect.width/scaleX;
//     var y = event.rect.height/scaleY;
//
//     //get data-x offsets of container
//     offset_left = target.getAttribute('data-x');
//     offset_top  = target.getAttribute('data-y');
//
//     x = checkBounds(offset_left, x, $('#pagecontainers').width())
//     y = checkBounds(offset_top, y, $('#pagecontainers').height())
//
//     target.style.width  = x + 'px';
//     target.style.height = y + 'px';
// }
//
// function checkBounds(offset, dimension, limit)
// {
//     offset = (parseFloat(offset) || 0);
//     if (offset + dimension > limit)
//     {
//         //larger than container
//         dimension = limit - offset
//     }
//     return dimension;
// }

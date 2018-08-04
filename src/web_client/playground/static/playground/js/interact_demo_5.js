var element = document.getElementById('yes-drop'),
    x = 0, y = 0;

// target elements with the "draggable" class
interact(element)
  .draggable({
    snap: {
      targets: [
        interact.createSnapGrid({ x: 30, y: 30 })
      ],
      range: Infinity,
      relativePoints: [ { x: 0, y: 0 } ]
    },
    // enable inertial throwing
    inertia: true,
    // keep the element within the area of it's parent
    restrict: {
      restriction: element.parentNode,
      endOnly: true,
      elementRect: { top: 0, left: 0, bottom: 1, right: 1 }
    },
    // enable autoScroll
    autoScroll: true,

    // call this function on every dragmove event
    onmove: dragMoveListener,
    // call this function on every dragend event
    onend: function (event) {
      var textEl = event.target.querySelector('p');

      textEl && (textEl.textContent =
        'moved a distance of '
        + (Math.sqrt(Math.pow(event.pageX - event.x0, 2) +
                     Math.pow(event.pageY - event.y0, 2) | 0))
            .toFixed(2) + 'px');
    }
  }).dropzone({
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

  },
  ondropdeactivate: function (event) {
    // remove active dropzone feedback
    event.target.classList.remove('drop-active');
    event.target.classList.remove('drop-target');
  }
});


  function dragMoveListener (event) {
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

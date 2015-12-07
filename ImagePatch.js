var EmailTo = "pagerk@gmail.com";
var MinimumImageWidth = 40;
var MinimumImageHeight = 40;
var DoneEditingButton = '\u2713'; // '\u263B'
var StartEditingButton = '\u263A';
var ButtonActiveColor = 'blue';
var ButtonInactiveColor = 'black';
var ButtonBlinkColor = 'red';
var BlinkRateInMilliseconds = 1000;
var ImagePatchTable = [
	"2006120100BadgerMasonM2003:48,41=Mason Badger",
	"1981000000PageMarcA1973:70,45=William Page:57,62=Amanda Page:49,19=Marc Page:30,40=Deborah Page",
	"1981080000PageDeborahA1976:70,24=Deborah Page:40,36=Amanda Page",
];

function distance(x1,y1,x2,y2) {
	return Math.sqrt( Math.pow(x1-x2,2) + Math.pow(y1-y2,2) );
}

function interpret(entry) {
	/* Returns
		{
			'identifier' : <image basename>,
			'people' : {
				'John Doe': {
					'x' : 50.0,
					'y' : 25.0,
					'radius' : 28.5,
				},
			},
		}
	*/
	var info = {};
	var parts = entry.split(':');
	info['identifier'] = parts[0];
	info['entry'] = entry;
	info['people'] = {};
	for(var i = 1; i < parts.length; ++i) {
		var person = parts[i].split('=');
		var name = person[1];
		var coords = person[0].split(",");
		info['people'][name] = {
			'x' : coords[0],
			'y' : coords[1],
		}
	}
	for(var person in info['people']) {
		var nearest = person;
		var best = 150.0; // longest distance possible in 100x100 square
		var px = info['people'][person]['x'];
		var py = info['people'][person]['y'];
		for(var other in info['people']) {
			if(other == person) {continue;}
			var ox = info['people'][other]['x'];
			var oy = info['people'][other]['y'];
			var dist = distance(px,py,ox,oy);
			if(dist < best) {
				best = dist;
				nearest = other;
			}
		}
		info['people'][person]['radius'] = best / 2.0;
	}
	return info;
}

function findPerson(info, image, event) {
	var r = image.getBoundingClientRect();
	var x = Math.round(100*(event.clientX - r.left)/r.width);
	var y = Math.round(100*(event.clientY - r.top)/r.height);
	for(var person in info['people']) {
		var px = info['people'][person]['x'];
		var py = info['people'][person]['y'];
		var r = info['people'][person]['radius'];
		var dist = distance(px,py,x,y);
		if( dist <= r ) {return person;}
	}
	return null;
}

function lookupImage(identifier) {
	var info = null;
	for(var i = 0; i < ImagePatchTable.length; ++i) {
		var info = interpret(ImagePatchTable[i]);
		if(identifier == info['identifier']) { return info;}
	}
}

function move(element) {
	var identifier = element.id.replace("img_","");
	var label = document.getElementById("label_"+identifier);
	var info = lookupImage(identifier);
	if(info) {
		var person = findPerson(info, element, window.event);

		if(person) {label.innerText = person;}
			else {label.innerText = "";}
	}
}

function click(element) {
	var identifier = element.id.replace("img_","");
	var button = document.getElementById("button_"+identifier);
	if(button.innerText == DoneEditingButton) {
		var person = prompt("Who is this?","Name");
		if(person.length > 0) {
			var store = document.getElementById("store_"+identifier);
			var e = window.event;
			var image = document.getElementById("img_"+identifier);
			var r = image.getBoundingClientRect();
			var x = Math.round(100*(e.clientX - r.left)/r.width);
			var y = Math.round(100*(e.clientY - r.top)/r.height);
			var prefix = "";
			if(store.value) {prefix = store.value+':';}
				else {prefix = identifier+':';}
			store.value = prefix+x+','+y+'='+person;
			button.style.color = ButtonActiveColor;
		}
	}
}

function edit(element) {
	var identifier = element.id.replace("button_","");
	var store = document.getElementById("store_"+identifier);
	var img = document.getElementById("img_"+identifier);
	var info = lookupImage(identifier);
	if(img.parentElement.tagName.toLowerCase() == "a") {
		var link = img.parentElement;
		if(!link.alt_href) {link.alt_href = link.href;}
		if(!link.alt_target) {link.alt_target = link.target;}
		if(element.innerText == DoneEditingButton) {
			link.href = link.alt_href;
			link.target = link.alt_target;
			element.style.color = ButtonActiveColor;
		} else {
			link.href = "#";
			link.target = "";
			element.style.color = ButtonInactiveColor;
		}
	}
	if(element.innerText == DoneEditingButton) {
		element.innerText = StartEditingButton;
		img.style.cursor="auto";
		if(store.value.length > 0 && (!info || store.value != info['entry'])) {
			window.location.href = "mailto:"+EmailTo+"?subject=Image%20Updated&body="+encodeURIComponent(store.value);
			store.value = "";
		}
	} else {
		element.innerText = DoneEditingButton;
		img.style.cursor="crosshair";
		if(info) {store.value = info['entry'];}
	}
}

function blink() {
	var buttons = document.getElementsByTagName("a");

	for(var i = 0; i < buttons.length; ++i) {
		var button = buttons[i];

		if(button.innerText == DoneEditingButton && (button.style.color == ButtonActiveColor || button.style.color == ButtonBlinkColor)) {
			button.style.color = button.style.color == ButtonActiveColor ? ButtonBlinkColor : ButtonActiveColor;
		}
	}
	setTimeout(function () {
		blink();
	}, BlinkRateInMilliseconds);
}

function patchUpImages() {
	var images = document.getElementsByTagName("img");

	for(var i = 0; i < images.length; ++i) {
		var image = images[i];
		var imageArea = image.getBoundingClientRect();
		if(imageArea.height < MinimumImageHeight || imageArea.width < MinimumImageWidth) {continue;}
		var pathParts = image.src.split("/");
		var identifier = pathParts[pathParts.length-1].split(".").slice(0,-1).join(".");
		var store = document.createElement("input");
		var button = document.createElement("a");
		var label = document.createElement("div");
		var container = image;
		if(container.parentElement.tagName.toLowerCase() == "a") {
			container = container.parentElement;
		}
		//store.setAttribute("type", "hidden");
		store.setAttribute("id", "store_"+identifier);
		store.setAttribute("type", "hidden");
		button.setAttribute("id", "button_"+identifier);
		button.setAttribute("style", "text-decoration:none; color:"+ButtonActiveColor+"; font-weight: bold; font-size:200%;");
		button.innerText = StartEditingButton;
		button.onclick = function () { edit(this); };
		label.setAttribute("id", "label_"+identifier);
		container.insertAdjacentElement("afterend",label);
		container.insertAdjacentElement("afterend",store);
		container.insertAdjacentElement("afterend",button);
		image.setAttribute("id","img_"+identifier);
		image.onclick = function () { click(this); };
		image.onmousemove = function () { move(this); };
	}
	blink();
}

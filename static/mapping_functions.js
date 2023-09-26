const data = {
    map_data: 'lat'
}

async function getData() {
    const res = await fetch(
        'http://127.0.0.1:8000/api-mapping/',
        {
            method: "POST",
            headers: {
                "Accept": "application/json",
            },
            body: JSON.stringify(data)
        }
    )
    return res.json()
}

async function map(){

    var myLines = [{
    "type": "LineString",
    "coordinates": [[-100, 40], [-105, 45], [-110, 55]]
}, {
    "type": "LineString",
    "coordinates": [[-105, 40], [-110, 45], [-115, 55]]
}];

    const wrf = await getData()

    const geojson = JSON.parse(wrf.geojson).features


    console.log(geojson)


    let map = L.map('map').setView([25, -87], 6);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 50,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);
    for (var i = 0; i < geojson.length; i++) {
        L.geoJSON(geojson[i], {
            style: {
                color: 'rgb(97,95,95)',
                opacity: 1,
                stroke: true,
                weight: 0.5,
                fillColor: geojson[i].properties.fill,
                fillOpacity: 0.2,
                className: geojson[i].properties.title,
                bubblingMouseEvents: true,
            },
        }).addTo(map);
    }

    function getColor(d) {
        return geojson[d].properties.fill;
	}

    function style(feature) {
		return {
			weight: 2,
			opacity: 1,
			color: 'white',
			dashArray: '3',
			fillOpacity: 0.7,
			fillColor: getColor(feature.properties.density)
		};
	}

    L.control.scale().addTo(map);

    const info = L.control();

    info.onAdd = function (map) {
		this._div = L.DomUtil.create('div', 'info');
		this._div.innerHTML = `<h4>Sea Level Pressure (hPa)</h4>`;
		return this._div;
	};


	info.addTo(map);

    // map.on('mousemove', function(e) {
    //     // console.log(e.latlng);
    //     let tooltip = L.tooltip([e.latlng.lat,e.latlng.lng],
    //         {
    //                     content: JSON.stringify(e.latlng),
    //                     sticky: true,
    //                 }).addTo(map);
    //     tooltip.mouseout(tooltip.close());
    // } );

    const legend = L.control({position: 'bottomright'});

	legend.onAdd = function (map) {

		const div = L.DomUtil.create('div', 'info legend');
		const grades = wrf.invert_lvl;
		const labels = [];
        const measurement = [`<h4>hPa</h4>`];
		let from, to;
        div.innerHTML = measurement;
		for (let i = 0; i < grades.length-1; i++) {
			from = grades[i];
			to = grades[i + 1];

			labels.push(`<i style="background:${getColor(i)}; opacity: 0.3;"></i> ${from}${to ? ` &ndash; ${to}` : '+'}`);
		}

		div.innerHTML = labels.join('<br>');
		return div;
	};

	legend.addTo(map);// var myStyle = {
}
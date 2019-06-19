var geocoder;
var map;
function initMap() {
    geocoder = new google.maps.Geocoder();
    var US_center = { lat: 39.50, lng: -98.35 };

    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 4,
        center: US_center
    });
    findPark(address);

}

function findPark(address) {
    geocoder.geocode({ 'address': address }, function (results, status) {
        var latLng = {lat: results[0].geometry.location.lat (), lng: results[0].geometry.location.lng ()};
        if (status == 'OK') {
            var marker = new google.maps.Marker({
                position: latLng,
                map: map
            });
        }
    });
}
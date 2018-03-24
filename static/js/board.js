$(document).ready(function(){
	var images = {};

	$('.image').click(function(event){
		this.style.width = this.naturalWidth+'px';
		if (images[this]) { 
			this.style.maxWidth = '100%';
			images[this] = false;
		} else {
			this.style.maxWidth = '200px';
			images[this] = true;
		}
	});
});

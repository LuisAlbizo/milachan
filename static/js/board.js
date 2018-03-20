$(document).ready(function(){
	function notify(message, type = 'info', icon = 'warning-sign', url = '#') {
		return $.notify(
			{
				message: message,
				icon: 'glyphicon glyphicon-'+icon,
				url: url
			},
			{
				newest_on_top: true,
				type: type,
				url_target: '_self'
			}
		)
	}

	function ajax_post() {
		$.ajax({
			url:"/"+board+"/post",
			type:"POST",
			data: new FormData($("#post-form")[0]),
			processData: false,
			contentType: false,
			enctype: "multipart/form-data",
			success:function(response){
				if (response.error){
					notify(response.type,'warning');
				}
				else {
					notify('Post enqueued','info');
				}
			},
			error:function(error){
				notify('Unknow Error','danger');
			}
		});
	}

	var uploading = false;

	$("#post-form").submit(function(event){
		if (!uploading) {
			uploading = true;
			event.preventDefault();
			ajax_post();
			document.forms["post-form"].reset();
			uploading = false;
		} else {
			notify("Already uploading","warning");
		}
	});

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

	var socket = io.connect('http://' + document.domain + ':' + location.port + '/boarding');

	socket.on('newPost',function(post){
		if (post.status){
			if (sha_id == post.data.ip){
				notify('Post uploaded','success','ok','/thread/'+post.data.board+'/'+post.data._id);
			}
			else {
				notify('New post: <a href="/thread/'+post.data.board+'/'+post.data._id+'">'+post.data.board+'#'+post.data._id+'</a>');
			}
		}
		else {
			if (sha_id == post.data.ip){
				notify('Post not uploaded','danger');
			}
		}
	});

});

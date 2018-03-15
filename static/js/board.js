$(document).ready(function(){
	function ajax_post() {
		$.ajax({
			url:"/"+board+"/post",
			//data:$("#post-form").serialize(),
			type:"POST",
			data:new FormData($("#post-form")[0]),
			contentType:false,
			processData:false,
			success:function(response){
				if (response.error){
					$.notify('Queue is full','warn');
				}
				else {
					$.notify('Post enqueued','info');
				}
			},
			error:function(error){
				$.notify('Unknow Error','error');
			}
		});
	}

	$("#post-form").submit(function(event){
		event.preventDefault();
		ajax_post();
	});

	var socket = io.connect('http://' + document.domain + ':' + location.port + '/boarding');

	socket.on('newPost',function(post){
		if (post.status){
			if (sha_id == post.data.ip){
				$.notify('Post uploaded','success');
			}
			else {
				$.notify('New post:'+post.data._id,'info');
			}
		}
		else {
			if (sha_id == post.data.ip){
				$.notify('Post not uploaded','error');
			}
		}
	});

});

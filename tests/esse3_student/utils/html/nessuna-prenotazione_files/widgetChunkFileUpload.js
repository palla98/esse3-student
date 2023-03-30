/*
 * Widget di file upload di esse3
 */
$(function () {
	
	var fileUploadXHR;
	var isRwd = $("#modalUpload").length ? true : false;
	
	var hideModalUpload = function(){
    	if (isRwd){
    		$("#modalUpload").modal('hide');
    		var progressBarText = document.getElementById('progressBarText');
        	if (progressBarText && progressBarText.parentNode) {
        		progressBarText.parentNode.removeChild(progressBarText);
        	}
    	} else {
    		var modal = document.getElementById('modalUploadNoRwd');
		    modal.style.display = "none";
    	}
	};
	
	
	$('button[data-dismiss="modal"]').on('click', function (e) {
		$('.fileupload').each(function () {
			fileUploadXHR.abort();
		});
	});
		
	$('.fileupload').each(function () {
	    $(this).fileupload({
	        dataType: 'json',
	        url: 'auth/ChunkUpload.do',
	        maxChunkSize: 2097152, // 2 MB
	        sequentialUploads: true,
	        multipart: false,
	        
	        add: function (e, data) {
	        	
	        	if (isRwd){
		        	$("#modalUpload").modal({
		        		show: true,
		                backdrop: 'static',
		                keyboard: false
		        	});
	        	} else {
	        		var modal = document.getElementById('modalUploadNoRwd');
	        		modal.style.display = "block";
	        		var span = document.getElementsByClassName("close")[0];
	        		// When the user clicks on <span> (x), close the modal
	        		span.onclick = function() {
	        		    modal.style.display = "none";
	        		    fileUploadXHR.abort();
	        		}
	        	}
	        	
	        	//Eliminazione messaggio di validazione relativo al file precedente
            	$('#' + this.id + '-div span.help-block').html(''); //rwd on
            	$('#' + this.id + '-div span.inputText-alertMessage').html(''); //rwd off
	        	
            	var progress = $('#' + this.id + '_progress');
	        	var progressBar = $('#' + this.id + '_progress .progress-bar');
	        	progressBar.removeClass('progress-bar-danger');
	        	var progressBarText = document.getElementById('progressBarText');
	        	if (progressBarText && progressBarText.parentNode) {
	        		progressBarText.parentNode.removeChild(progressBarText);
	        	}
	        	progress.prepend('<span id="progressBarText">' + chunkUploadMsgStartingUpload + ' - 0%</span>');
	        	progressBar.css('width', '0%');
	        	var url = 'auth/ChunkUploadStart.do';           
	            
	            var dataToSend = {};
	        	dataToSend.filename = data.files[0].name;
	        	
	        	var fieldId = this.id;

	            $.post(url, dataToSend, function (result) {
	            	var progressBar = $('#' + fieldId + '_progress .progress-bar');
	            	progressBar.css('width','10%');
	            	fileUploadXHR = data.submit();
	            }).fail(function () {
	            	var progressBarText = $('#progressBarText');
	            	progressBarText.text(chunkUploadMsgErrorStarting);
	            	var progressBar = $('#' + fieldId + '_progress .progress-bar');
	        		progressBar.css('width','100%');
	        		progressBar.addClass('progress-bar-danger');
		        	$.getJSON('auth/ChunkUploadError.do');
	            }, "json");
	            
	        },
	        done: function (e, data) {
	        	var progressBar = $('#' + this.id + '_progress .progress-bar');
	        	var id = this.id;
	        	
	        	var url = 'auth/ChunkUploadEnd.do';
	        	
	        	var dataToSend = {};
	        	dataToSend.filename = data.files[0].name;
	        	
	        	var progressBarText = $('#progressBarText');
	        	progressBarText.text(chunkUploadMsgSaving + ' - 80%');
	        	
	        	var fnSavingProgress = function() {
		        	var progressBarText = $('#progressBarText');
		        	var percent = Number(progressBarText.text().slice(-3, -1));
		        	if (percent < 99) {
		        		progressBarText.text(chunkUploadMsgSaving + ' - ' + (percent + 1) + '%');
		        		progressBar.css('width', (percent + 1) + '%');
		        	}
	        	}
	        	var interval = 800;
	        	if (data.total > 100000000) {
	        		interval = 800 + (1200 * data.total / 500000000);
	        	}
	        	var savingProgress = setInterval(fnSavingProgress, interval);
	        	
	            $.post(url, dataToSend, function (result) {
	            	clearInterval(savingProgress);
	            	
	            	progressBarText.text(chunkUploadMsgCompleted + ' - 100%');
	            	progressBar.css('width','100%');
	            	$('#uploadedFile').html($('<p/>').text(data.files[0].name));
	            	setTimeout(hideModalUpload, 500);
	            	
	            	var inputAllegatoId = $('input[name="allegato_id"]');
	            	if (inputAllegatoId.length > 0){
	            		inputAllegatoId[0].value = result.allegatoId;
	            	} else {
	            		$('<input>').attr({
	            			type: 'hidden',
	            			id: 'allegato_id',
	            			name: 'allegato_id',
	            			value: result.allegatoId
	            		}).appendTo($('#'+id)[0].form);
	            	}
	            	
	            }).fail(function () {
	            	clearInterval(savingProgress);
	            	
	            	progressBarText.text(chunkUploadMsgErrorSaving);
	        		progressBar.css('width','100%');
	        		progressBar.addClass('progress-bar-danger');
		        	$.getJSON('auth/ChunkUploadError.do');
	            }, "json");
	        },
	        fail: function (e, data) {
	        	var progressBar = $('#' + this.id + '_progress .progress-bar');
	        	var progressBarText = $('#progressBarText');
	        	$.getJSON('auth/ChunkUploadError.do', function (result) {
	        		progressBarText.text(chunkUploadMsgErrorUploading);
	        		progressBar.css('width','0%');
	        	});
	        },
		    progressall: function (e, data) {
		        var progress = parseInt(data.loaded / data.total * 100, 10);
		        progress = parseInt((progress / 100 * 70) + 10); //Scalo su 70% (10 start e 20 end)
		        $('#progressBarText').text(chunkUploadMsgUploading + ' - ' + progress + '%');
		        var progressBar = $('#' + this.id + '_progress .progress-bar');
		        progressBar.css(
		            'width',
		            progress + '%'
		        );
		    }
	    });
    });
});
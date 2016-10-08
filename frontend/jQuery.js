function getUrlVars() {
	var vars = {};
	var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
		vars[key] = value;
	});
	return vars;
}


var server = "http://localhost:5000";
$(document).ready(function(){
	$("#emailInput").focus();
	$(document).keypress(function(e){
		if (e.which == 13){
			var email = $("#emailInput").val();
			$.get(server + "/getUserId?email="+email,function(data){
				serverRepply=JSON.parse(data);
				var userID = serverRepply.id;
				endEmail(userID,email);
				$(document).off("keypress");
			});
		}
	});
});

function endEmail(userID,email){
	urlVars=getUrlVars();
	if ("id" in urlVars){
		var roomID = urlVars["id"];
		$.get(server + "/joinRoom?idRoom="+roomID+"&email="+email);
		startQuestions(userID,roomID)
	}
	else{
		startAdmin(userID);
	}
}

function startQuestions(userID, roomID){
	$("#emailContainer").fadeOut();

	var questions;

	$("#questionContainer").fadeIn();
	//shitty way to do this
	$.get(server+"/getRoomQuestion?idRoom="+roomID+"&idUser="+userID, function(data){
		serverRepply=JSON.parse(data);
		questions=serverRepply.questions;
		var answers=[];
		setQuestions(userID,roomID,questions,answers,0);
	});
}

function setQuestions(userID,roomID,questions,answers,i){
	$("#answerInput").val("").focus();
	if (i==questions.length){
		console.log(answers);
		console.log(userID);
		$.ajax({
            url:server+"/postRoomAnswers",
            data:JSON.stringify({
				idRoom:roomID,
				idUser:userID,
				answers:answers
			}),
			contentType:"application/json; charset=utf-8",
			type:"POST"
		});
	}
	else{
		$("#questionText").text(questions[i].text);
		$(document).keypress(function(e){
			if (e.which==13){
				answers[i]={
					id:questions[i].id,
					text:$("#answerInput").val()
				};
				$(document).off("keypress");
				setQuestions(userID,roomID,questions,answers,i+1);
			}
		});
	}
}

function startAdmin(userID){
	$("#emailContainer").fadeOut();
	$("#adminContainer").fadeIn();
	$("#newRoom").click(function(){newRoom(userID)});
}

function newRoom(userID){
	$("#adminContainer").fadeOut();
	$("#newRoomContainer").fadeIn();
	newQuestions=[];
	$(document).keypress(function(e){
		if (e.which==13){
			newQuestions.push($("#questionInput").val());
			$("#questionInput").val("");	
		}
	});
	$("#finishRoom").click(function(){
		$.get(server+"/createRoom?userId="+userID,function(data){
			serverRepply=JSON.parse(data);
			roomID=serverRepply.id;
			$.ajax({
	            url:server+"/fillRoom",
	            data:JSON.stringify({
	            	id:roomID,
					question:newQuestions
				}),
				contentType:"application/json; charset=utf-8",
				type:"POST"
			});
			$("#questionInput").val("");
			$(document).off("keypress");
			$("#finishRoom").off("click");
			$("#cancelRoom").off("click");
			$("#newRoomContainer").fadeOut();
			$("#adminContainer").fadeIn();
		});
	});
	$("#cancelRoom").click(function(){
			$("#questionInput").val("");
			$(document).off("keypress");
			$("#finishRoom").off("click");
			$("#cancelRoom").off("click");
			$("#newRoomContainer").fadeOut();
			$("#adminContainer").fadeIn();
	});

}
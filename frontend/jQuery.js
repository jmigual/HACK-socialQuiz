function getUrlVars() {
	var vars = {};
	var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
		vars[key] = value;
	});
	return vars;
}


var server = "http://localhost:5000";
var server2 = "http:interact.siliconpeople.net"
$(document).ready(function(){
	$("#emailInput").focus();
	$(document).keypress(function(e){
		if (e.which == 13){
			var email = $("#emailInput").val();
			console.log('hi');
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
		$("#questionContainer").fadeOut();
		$("#quizQuestionContainer").fadeIn();
		startQuiz(userID,roomID);
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

	var preToggle="<div class=\"checkbox\"><label><input type=\"checkbox\" data-toggle=\"toggle\" id=\"";
	var midToggle="\">";
	var postToggle="</label></div>";

	$.get(server+"/getRooms?userId="+userID,function(data){
		serverRepply=JSON.parse(data);
		var rooms= serverRepply.rooms;
		for (var i=0; i<rooms.length; i++){
			var r=rooms[i];
			$("#checkboxContainer").append(preToggle+r+midToggle+r+postToggle);

			$.get(server+"/statusRoom?id="+r,function(data){
				serverRepply=JSON.parse(data);
				var open='off';
				if (serverRepply.status == "started") open='on';
				$("#"+r).bootstrapToggle({
					on: 'Open',
					off: 'Closed'
				}).bootstrapToggle(open).change(function(){
					if($(this).prop('checked')){
						console.log(server+"/openRoom?id="+r);
						$.get(server+"/openRoom?id="+r,function(data){});
					}
					else{
						console.log(server+"/closeRoom?id="+r);
						$.get(server+"/closeRoom?id="+r,function(data){});
					}
				});
			});
		}
	});
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
			alert(roomID);
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

function startQuiz(userID, roomID){

	var buttonPre="<button type=\"button\" style=\"width: 100%\" class=\"btn btn-default\" id=\"";
	var buttonMid="\">";
	var buttonPost="</button>";

	$.get(server+"/getQuizQuestion?idRoom="+roomID+"&idUser="+userID,function(data){
		serverRepply=JSON.parse(data);
		quizQuestionID=serverRepply.id;
		quizQuestionText=serverRepply.question;
		quizAnswers=serverRepply.answers;
		$("#quizQuestionText").text(quizQuestionText);
		$.each(quizAnswers,function(i,value){
			$("#quizAnswerColumn").append(buttonPre+value.id+buttonMid+value.text+buttonPost)
			$("#"+value.id).click(function(){answerQuiz(quizQuestionID,value.id,userID,roomID)});
		});
	});


}

function answerQuiz(questionID,answerID,userID,roomID){
	$("#quizAnswerColumn").empty();
	$.get(server+"/postAnswer?quizQuestionId="+questionID+"&answerID="+answerID,function(data){
		serverRepply=JSON.parse(data);
		if (serverRepply.correct=="true"){
			alert("Correct answer");
		}
		else{
			alert("Incorrect answer\n the right answer was: "+serverRepply.correctAnswer.text);
		}
		startQuiz(userID,roomID);
	});
}
$(function(){
	$("#validate").submit(function(evt) {
		evt.preventDefault()
		$(".content").animate({
			top: -250
		});
		$(".list-erros").fadeIn("slow");
	});
});

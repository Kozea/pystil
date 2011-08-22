(function(){var a,b,c,d,e=Object.prototype.hasOwnProperty,f=function(a,b){function d(){this.constructor=a}for(var c in b)e.call(b,c)&&(a[c]=b[c]);return d.prototype=b.prototype,a.prototype=new d,a.__super__=b.prototype,a},g=function(a,b){return function(){return a.apply(b,arguments)}};b=function(){var a,b,c;if($("#last-visits").length)return a=0,c=function(){return $.ajax({url:location.href+"/*/"+a+"/last_visits.json",method:"GET",dataType:"json",success:b})},b=function(b){var d,e,f,g;g=b.list;for(e=0,f=g.length;e<f;e++)d=g[e],$("#last-visits tbody").prepend($("<tr>").append($("<td>").text(d.host)).append($("<td>").text(d.ip)).append($("<td>").text(d.country)).append($("<td>").text(d.city)).append($("<td>").text(d.page)).append($("<td>").text(d.referrer)));return a=b.stamp,setTimeout(c,2e3)},$.ajax({url:location.href+"/*/last_visits.json",method:"GET",dataType:"json",success:b})},$(b),c=function(){var a;if($("#map").length)return $("body").append($("<div>").attr("id","tooltip").css({position:"absolute",display:"none"})),$(".country").mouseover(function(a){return $("#tooltip").css({top:a.pageY+10+"px",left:a.pageX+10+"px",display:"block"}).text($("title",a.currentTarget).text())}),$(".country").mouseout(function(a){return $("#tooltip").css({display:"none"})}),a=function(a){var b,c,d,e,f;e=a.list,f=[];for(c=0,d=e.length;c<d;c++)b=e[c],f.push($("#"+b.key.split("$")[1].toLowerCase()).css({fill:"rgba(0, 0, 255, "+(b.count/a.max*.7+.2)+")"}).prepend($("<title>").text(b.key.split("$")[0].toLowerCase()+": "+b.count)));return f},$.ajax({url:location.href+"_by_visit.json",method:"GET",dataType:"json",success:a})},$(c),d=location.pathname+"/",this.Graph=function(){function a(a){this.name=a}return a.prototype.root=d,a.prototype.url=function(){return d+this.type+"_by_"+this.name+".json"},a}(),this.Line=function(){function a(){a.__super__.constructor.apply(this,arguments)}return f(a,this.Graph),a.prototype.type="line",a.prototype.options={lines:{show:!0,fill:!0},points:{show:!0,fill:!0},grid:{hoverable:!0},xaxis:{mode:"time",timeformat:"%y-%0m-%0d"},yaxis:{tickDecimals:0}},a.prototype.data=function(a){return a.series},a.prototype.tooltip=function(a){var b,c;return c=a.datapoint[1],b=new Date(a.datapoint[0]),c+" "+a.series.label.toLowerCase()+" on "+b.getFullYear()+"-"+(b.getMonth()+1)+"-"+b.getDate()},a}.call(this),this.Bar=function(){function a(){a.__super__.constructor.apply(this,arguments)}return f(a,this.Graph),a.prototype.type="bar",a.prototype.options={bars:{show:!0,fill:!0},grid:{hoverable:!0},xaxis:{min:0,max:23,ticks:24,tickDecimals:0},yaxis:{tickDecimals:0}},a.prototype.data=function(a){return[a]},a.prototype.tooltip=function(a){var b,c;return b=a.datapoint[0],c=a.datapoint[1],c+" visits at "+b+" h"},a}.call(this),this.TimeBar=function(){function a(){a.__super__.constructor.apply(this,arguments)}return f(a,this.Bar),a.prototype.options={bars:{show:!0,fill:!0},grid:{hoverable:!0},xaxis:{min:0,max:60,tickDecimals:0},yaxis:{tickDecimals:0}},a.prototype.tooltip=function(a){var b,c;return b=a.datapoint[0],c=a.datapoint[1],c+" visits during between "+b+" and  "+(b+1)+" minutes"},a}.call(this),this.Pie=function(){function a(){a.__super__.constructor.apply(this,arguments)}return f(a,this.Graph),a.prototype.type="pie",a.prototype.options={grid:{hoverable:!0},series:{pie:{show:!0}}},a.prototype.data=function(a){return a.list},a.prototype.tooltip=function(a){var b;return b=a.datapoint[0],a.series.label+": "+b.toFixed(1)+"%"},a}.call(this),a=g(function(){var a,b,c,d,e,f,g,h,i;h=$(".graph"),i=[];for(f=0,g=h.length;f<g;f++)b=h[f],a=$(b),a.hasClass("pie")?c=new this.Pie(b.id):a.hasClass("line")?c=new this.Line(b.id):a.hasClass("bar")&&(a.hasClass("time")?c=new this.TimeBar(b.id):c=new this.Bar(b.id)),a.addClass("loading"),e=function(a,b){return function(c){return b.removeClass("loading"),$.plot(b,a.data(c),a.options)}}(c,a),$.ajax({url:c.url(),method:"GET",dataType:"json",success:e}),d=null,i.push(a.bind("plothover",function(a){return function(b,c,e){var f;if(!e)return $("#tooltip").remove(),d=null;f=e.series.pie.show?e.seriesIndex:e.dataIndex;if(d!==f)return d=f,$("#tooltip").remove(),$("<div>").attr("id","tooltip").css({top:c.pageY+5,left:c.pageX+5,border:"1px solid "+e.series.color}).text(a.tooltip(e)).appendTo("body")}}(c)));return i},this),$(a)}).call(this)
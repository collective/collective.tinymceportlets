var overlay_selector = '#pb_9991';
var overlay_content_selector = overlay_selector + ' .pb-ajax .overlaycontent';
var content_selector = overlay_content_selector;
var selected_checkbox = null;
var checkTimout = null;

function checkContextCheckChange(){
  if($(content_selector).length == 0){
    return;
  }
  var selected = $('#form-widgets-context-input-fields input:checked');
  if(selected.length > 0){
    var id = selected.attr('id');
    if(selected_checkbox != id){
      selected_checkbox = id;
      loadOverlay(getOverlayConfig());
    }
  }
  checkTimout = setTimeout(checkContextCheckChange, 500);
}

$('body').append('<div id="pb_9991" class="overlay overlay-ajax "><div class="close"><span>Close</span></div><div class="pb-ajax"><div class="overlaycontent"></div></div></div>');

$("#pb_9991").overlay({
    onClose : function(){
        $(overlay_content_selector).html('');//clear it
    }
});

function getOverlayConfig(){
  var context_input = $('input[name="form.widgets.context:list"]:checked');
  return { 
    context : context_input.val(),
    context_ele : context_input.closest('span.option').clone(),
    portlet : $('#form-widgets-portlet').val()
  }
}

function portletHash(){
  return $('#form-widgets-portlet option:selected').val();
}

function decodeHash(hash){
  var split = hash.split('-', 2);
  var rest = hash.split('-');
  return {
    manager : split[0].replace(' ', ''),
    portlet : split[1].replace(' ', ''),
    context : rest.slice(2).join('-')
  }
}

function loadOverlay(selected){
  var qs = '';
  var context = false;
  var portlet = false;
  
  ed = tinyMCE.activeEditor;
  if(ed == null){
    return;
  }
  item = ed.selection.getNode();
  jqitem = $(item);

  isCurrentPortlet = function(){
    return (jqitem.length > 0 && jqitem.hasClass('mce-only'));
  }
  
  if(isCurrentPortlet() && selected == undefined){
    var hash = jqitem[0].className.replace('mce-only', '').replace('TINYMCEPORTLET', '').replace(' ', '')
    selected = decodeHash(hash);
  }
  
  if(selected != undefined){
    qs = '?';
    context = selected.context
    qs += '&context=' + context;
    portlet = selected.portlet;
    qs += '&portlet=' + portlet
  }
  
  
  var wrap = $(overlay_content_selector);
  var url = $('base').attr('href') + '/@@add-tinymce-portlet' + qs;
  $('#kss-spinner').show();
  jq.ajax({
    url : url, 
    success: function(data, textStatus, req){
      wrap.html(data);

      if(isCurrentPortlet()){
      
      }else{
        $(content_selector + ' input[name="form.buttons.save"]').attr('value', 'Add');
        $(content_selector + ' input[name="form.buttons.remove"]').hide();
      }
      if(context != false){
        var input = $(content_selector + ' input[value="' + context + '"]');
        if(input.length > 0){
          input[0].checked = true;
        }else{
          if(selected.context_ele != undefined && selected.context_ele.length > 0){
            input = selected.context_ele;
            input.find('input')[0].checked = true;
            $('#form-widgets-context-input-fields').append(input);
          }
        }
      }
      if(portlet != false){
        var input = $('#form-widgets-portlet input[value="' + portlet + '"]');
        if(input.length > 0){
          input[0].checked = true;
        }else if(selected.context_ele == undefined){
          $("#form-widgets-portlet").html('<option value="' + portlet + '" id="form-widgets-portlet-0">' + portlet + '</option>');
        }
      }

      $('#form-widgets-portlet').after('<a href="#" id="refresh-portlet-list"> Refresh List</a>');
      $('#refresh-portlet-list').after(
        '<br /><a target="_blank" href="' +
        $('base').attr('href') + '/@@manage-tinymceportlets">Add/Remove Tiny MCE Portlets</a>');

      clearTimeout(checkTimout);
      checkContextCheckChange();
      $('#kss-spinner').hide();
    }
  });
  $(overlay_selector).overlay().load();
}

$(content_selector).delegate('input[name="form.buttons.save"]', 'click', function(){
  var node = tinyMCE.activeEditor.selection.getNode();
  var item = $(node);
  if(item.length > 0 && item.hasClass('mce-only')){
    item[0].className = "TINYMCEPORTLET mce-only " + portletHash();
  }else{
    item.append('<img class="TINYMCEPORTLET mce-only ' + portletHash() + '" src="++resource++collective.tinymceportlets/add-portlets.png" />');
  }
  $(overlay_selector).overlay().close();
});

$(content_selector).delegate('input[name="form.buttons.cancel"]', 'click', function(){
  $(overlay_selector).overlay().close();
  return false;
});

$(content_selector).delegate('input[name="form.buttons.remove"]', 'click', function(){
  var node = tinyMCE.activeEditor.selection.getNode();
  var item = $(node);
  item.remove();
  $(overlay_selector).overlay().close();
});

$(content_selector).delegate('#refresh-portlet-list', 'click', function(){
  loadOverlay(getOverlayConfig());
  return false;
});

$(content_selector).delegate('form#form', 'submit', function(){ return false; });

(function() {
  tinymce.create('tinymce.plugins.PortletsPlugin', {
    init : function(ed, url) {
      // Register the command so that it can be invoked by using tinyMCE.activeEditor.execCommand('mceExample');
	    ed.addCommand('mceportlets', function() {
		    try{
          loadOverlay();
		    }catch(e){
		      alert('Whoops. Something went wrong!');
		    }
      });

	    // Register example button
	    ed.addButton('mceportlets', {
		    title : 'Add/Edit portlet here.',
		    cmd : 'mceportlets',
		    image : url + '/add-portlets.png'
	    });
	  }
  });
  tinymce.PluginManager.add('mceportlets', tinymce.plugins.PortletsPlugin);
})();
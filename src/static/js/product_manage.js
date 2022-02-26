(function ($) { 
    $(document).ready(function(){

        if($('#id_is_varient').is(':checked')==false & $('#id_has_varient').is(':checked')==false){
            $('#id_parent').val(null)
            $('.field-parent').hide()
        }
        function hidebutton(params) {
            console.log('calling---')
            if($('#id_is_varient').is(':checked')){
                $('.field-has_varient').hide()
                $('.field-parent').show()
    
            }
            else{
                $('.field-has_varient').show()
                $('#id_parent').val(null)
                $('.field-parent').hide()
            }
            if($('#id_has_varient').is(':checked')){
                $('.field-is_varient').hide()
                $('#id_parent').val(null)
                $('.field-parent').hide()
            }
            else{
                $('.field-is_varient').show()
                $('.field-parent').show()
            }
        }

        $('#id_is_varient').click(function() {
            hidebutton()
            if($('#id_is_varient').is(':checked')){
                $('.field-product_tag').hide()
                $('.field-product_tag').val(null)
            }
            else{
                $('.field-product_tag').show()
            }
        })
        $('#id_has_varient').click(function() {
            hidebutton()
        })
        
        // $(document).on('change','#id_category', function (e) { 
        //     // e.preventdefault();
        //     console.log('changed',$(this).val());
        //     let product_attribute_list = []
        //     let tag_list = []
        //     $('#id_varient_property').children('option').each(function(){
        //         if($(this).attr('selected')){
        //             product_attribute_list.push($(this).prop('value')) ;
        //         }
        //     });
        //     $('#id_product_tag').children('option').each(function(){
        //         if($(this).attr('selected')){
        //             tag_list.push($(this).prop('value')) ;
        //         }
        //     });
        //     console.log(product_attribute_list);
        //     console.log(tag_list);
        //     $.ajax({
        //         type: "GET",
        //         url: "/change_product_tag_m2m_admin/",
        //         data: {'category_id':$(this).val()},
        //         success: function (response) {
        //             $('#id_product_tag').html(response)
        //             // console.log(response,'===========');
        //             $('#id_product_tag').children('option').each(function(){
        //                 if(tag_list.includes($(this).prop('value'))){
        //                     $(this).attr('selected','selected');
        //                 }
        //             });
        //         }
        //     });
        //     $.ajax({
        //         type: "GET",
        //         url: "/change_product_attribute_m2m_admin/",
        //         data: {'category_id':$(this).val()},
        //         success: function (response) {
        //             $('#id_varient_property').html(response)
        //             // console.log(response,'++++++++++');
        //             $('#id_varient_property').children('option').each(function(){
        //                 if(product_attribute_list.includes($(this).prop('value'))){
        //                     $(this).attr('selected','selected');
        //                 }
        //             });
        //         }
        //     });
        //  })
   
    })
    
 })(django.jQuery);
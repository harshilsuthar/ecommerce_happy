// (function ($) { 
//     $(document).on('change','#id_category', function (e) { 
//         // e.preventdefault();
//         console.log('changed',$(this).val());
//         let product_attribute_list = []
//         let tag_list = []
//         $('#id_productAttribute').children('option').each(function(){
//             if($(this).attr('selected')){
//                 product_attribute_list.push($(this).prop('value')) ;
//             }
//         });
//         $('#id_tagName').children('option').each(function(){
//             if($(this).attr('selected')){
//                 tag_list.push($(this).prop('value')) ;
//             }
//         });
//         console.log(product_attribute_list);
//         console.log(tag_list);
//         $.ajax({
//             type: "GET",
//             url: "/update_product_tag_name_list/",
//             data: {'category_id':$(this).val()},
//             success: function (response) {
//                 $('#id_tagName').html(response)
//                 // console.log(response,'===========');
//                 $('#id_tagName').children('option').each(function(){
//                     if(tag_list.includes($(this).prop('value'))){
//                         $(this).attr('selected','selected');
//                     }
//                 });
//             }
//         });
//         $.ajax({
//             type: "GET",
//             url: "/update_product_attribute_name_list/",
//             data: {'category_id':$(this).val()},
//             success: function (response) {
//                 $('#id_productAttribute').html(response)
//                 // console.log(response,'++++++++++');
//                 $('#id_productAttribute').children('option').each(function(){
//                     if(product_attribute_list.includes($(this).prop('value'))){
//                         $(this).attr('selected','selected');
//                     }
//                 });
//             }
//         });
//     })
// })(django.jQuery);
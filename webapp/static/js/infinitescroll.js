added = 0
window.onscroll = function() {
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 400) {
        $.get("/scroll_ep", function(data, _){
            dataP = JSON.parse(data.replaceAll("'", "\""));
            if (dataP[4].toLowerCase().includes('plant')){
                return
            }
            elem = document.createElement("div")
            if (added % 2 == 0){
                elem.innerHTML = `<div class="row gx-0 mb-5 mb-lg-0 justify-content-center aos-init aos-animate" data-aos="fade-left">
                        <div class="col-lg-6"><img class="img-fluid" src="${dataP[5]['url']}" alt="${dataP[0]}" style="width:100%"></div>
                        <div class="col-lg-6">
                            <div class="bg-black text-center h-100 project">
                                <div class="d-flex h-100">
                                    <div class="project-text w-100 my-auto text-center text-lg-left">
                                        <h4 class="text-white"><a href='${dataP[1]['url']}' style='color:white'>${dataP[0]}</a></h4>
                                        <p class="mb-0 text-white-50" style="padding: 10px">Scientific Name: ${dataP[1]['value']}<br>Status: ${dataP[2]}<br>Listed: ${dataP[3]}<br><br>Image found on <a href='https://ecos.fws.gov' style='color:white'>ecos.fws.gov</a>. Rights to: ${dataP[6]}</p>
                                        <hr class="d-none d-lg-block mb-0 ms-0">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>`
            } else{
                elem.innerHTML = `<div class="row gx-0 justify-content-center aos-init aos-animate" data-aos="fade-right">
                    <div class="col-lg-6"><img class="img-fluid" src="${dataP[5]['url']}" alt="${dataP[0]}" style="width:100%"></div>
                    <div class="col-lg-6 order-lg-first">
                        <div class="bg-black text-center h-100 project">
                            <div class="d-flex h-100">
                                <div class="project-text w-100 my-auto text-center text-lg-right">
                                    <h4 class="text-white"><a style='color:white' href='${dataP[1]['url']}'>${dataP[0]}</a></h4>
                                    <p class="mb-0 text-white-50" style="padding: 10px">Scientific Name: ${dataP[1]['value']}<br>Status: ${dataP[2]}<br>Listed: ${dataP[3]}<br><br>Image found on <a href='https://ecos.fws.gov' style='color:white'>ecos.fws.gov</a>. Rights to: ${dataP[6]}</p>
                                    <hr class="d-none d-lg-block mb-0 me-0">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>`
            }
            document.querySelector("#scrollContainer").appendChild(elem);
            added += 1;
            AOS.init();
        });
    }
};
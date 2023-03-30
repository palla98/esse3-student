/**
 * Indicatore di caricamento dei dei messaggi in lingua relativi alla validazione dell'IBAN.
 * Vedi template inputText.xsl
 */
var ibanSetLanguageLoaded=0;

/**
* Per nascondere o mostrare un elemento html identificato tramite il suo id
*/
function hideShowElemById(elemId){
	var elem = document.getElementById(elemId);
	if(elem){
		var hide = (elem.style.display=='none');
		if (hide){
			elem.style.display = '';
		} else {
			elem.style.display = 'none';
		}
	}
}

/**
* Per aggiungere o eliminare una classe da un elemento html
* @param 'cls' elementi html sui quali applicare l'add/remove della classe
* @param 'elem' classe di cui fare l'add/remove
* 
* hasClass(cls,elem): ritorna true o false a seconda se all'elemento html 'elem' è associata o meno la classe 'cls'
* addClass(cls,elem): associa all'elemento html 'elem' la classe 'cls'
* removeClass(cls,elem): rimuove dall'elemento html 'elem' la classe 'cls'
*/
function hasClass(cls,elem) {
	return elem.className.match(new RegExp('(\\s|^)'+cls+'(\\s|$)'));
}
 
function addClass(cls,elem) {
		elem.className = elem.className+' '+cls;
}
 
function removeClass(cls,elem) {
		var reg = new RegExp('(\\s|^)'+cls+'(\\s|$)');
		elem.className=elem.className.replace(reg,' ');
}

/**
* Sostituisce una classe dell'elemento html con la corrispontente classe di switch.
* Es. <a href="#" class="miaclasse">mio link</a> diventa <a href="#" class="miaclasse-switch">mio link</a> 
* e viceversa, dove miaclasse e miaclasse-switch solitamente definiscono comportamenti contrapposti
*
* @param 'elemIdList' lista degli elementi html sui quali applicare lo switch
* @param 'elemClassList' lista delle classi da switch-are
*/
function switchClass(elemIdList, elemClassList) {
	var arrElemClass = new Array(); 
	var arrElemId = new Array(); 
	var index = 0;
	var elemId;
	var elemClass;
    var elem =  new Array(); 
    
	arrElemClass= elemClassList.split(',');

	if (elemIdList != '') { 
		arrElemId= elemIdList.split(',');
		for (var j=0;j<arrElemId.length;j++){
			elem[j]= document.getElementById(arrElemId[j]);
		} 
	}
	else { 
		elem = document.getElementsByTagName('*');
	}

    while (typeof arrElemClass[index] != 'undefined' && arrElemClass[index] != null && arrElemClass[index] != '') {
		elemClass = arrElemClass[index];
		for (var i=0;i<elem.length;i++){
		  if (elem[i].getAttribute('id')!=null) {
			 if (hasClass(elemClass,elem[i])){
				 addClass(elemClass+'-switch',elem[i]);
				 removeClass(elemClass,elem[i]);
			 }
			 else if (hasClass(elemClass+'-switch',elem[i])) {
				 addClass(elemClass,elem[i]);
				 removeClass(elemClass+'-switch',elem[i]);
			 }
		  }
		}
		index = index+1;
	}
}

/**
* Effettua lo shift degli elementi di un container del DOM di uno step inter, visualizzando numVis elementi a partire dal 
* parametro start; vengono sempre visualizzati i primi numSkipFirst elementi e gli ultimo numSkipLast elementi
*/
function shiftContainerView(container, step, numVis, start, useMarker, numSkipFirst, numSkipLast){
	var elem = container.childNodes;
	var currElem=0;
	var elements = new Array();
	var idx=0;
	var currElem=container.getAttribute('currentElem');
	
	if(!currElem){
		currElem=start-1;
	}
	currElem=parseInt(currElem)+step;
	container.setAttribute('currentElem',currElem);	
	for(var i=0;i<elem.length;i++){
		if(elem[i].tagName){
			if(elem[i].tagName){
				elements[idx++]=elem[i];
			}
		}
	}
	
	var prevButton=numSkipFirst;
	var nextButton=elements.length-1-numSkipLast;

	var firstElem=prevButton+1;
	var lastElem=nextButton-1;
	if(useMarker) {
		firstElem++;
		lastElem--;
	}
	// pulsanti di spostamento avanti/indietro da nascondere se si arriva all'inizio/fine della lista
	if(currElem>firstElem){
		showElement(elements[prevButton]);
		if(useMarker){
			showElement(elements[prevButton+1]);
		}
	} else {
		hideElement(elements[prevButton]);
		if(useMarker){
			hideElement(elements[prevButton+1]);
		}
	}
	if(currElem>=lastElem-numVis+1){
		hideElement(elements[nextButton]);
		if(useMarker){
			hideElement(elements[nextButton-1]);
		}
	} else {
		showElement(elements[nextButton]);
		if(useMarker){
			showElement(elements[nextButton-1]);
		}
	}
	//si nascondono i nodi fuori dall'intervallo di visualizzazione
	for(var i=firstElem;i<=lastElem;i++){
		if(i<currElem || i>=currElem+numVis){
			hideElement(elements[i]);
		} else {
			showElement(elements[i]);
		}
	}
}
/*
 * Funzione che nasconde un elemento del DOM applicando la classe hiddenElem
 */
function hideElement(element){
	if(element.className.indexOf('hiddenElem')<0){
		if(element.className==''){
			element.className = 'hiddenElem';
		} else {
			element.className = element.className + ' hiddenElem';
		}
	}
}
/*
 * Funzione che ripristina la visualizzazione un elemento del DOM rimuovendo la classe hiddenElem
 */
function showElement(element){
	if(element.className.indexOf('hiddenElem')>=0){
		element.className = element.className.replace('hiddenElem',"");
	}
}

/**
* Gestione della visualizzazione della gif animata in corrispondenza dell'onChange di una select 
*/

function reloadForm(form) {
	document.getElementById(form.id + "_loading").style.display='block';
	$('#' + form.id).trigger('submit');
}

function reloadFormWithRefresh(form, id) {
	document.getElementById(form.id + "_loading").style.display='block';
	var el = document.createElement("input");
	el.type = "hidden";
	el.name = "_fw_refresh-form.x";
	el.value = id;
	form.appendChild(el);
	$('#' + form.id).trigger('submit');
}


/**
* Gestione del caricamento di un campo di input di tipo select con id cmbName con i dati recuperati dalla look up indicata in vUrl
*/

var CMB_NAME_HIDDEN_FIELD = '#*HIDDENfIELD*#';

function loadCombo(vUrl, cmbName){
  var nameCmb = document.getElementById(CMB_NAME_HIDDEN_FIELD);
  if(!nameCmb){
    nameCmb = document.createElement('input');
    nameCmb.setAttribute('id', CMB_NAME_HIDDEN_FIELD);
    nameCmb.setAttribute('type', 'hidden');
    document.forms[0].appendChild(nameCmb);
  }
  nameCmb.value=cmbName;
  var url = vUrl + "&tmp=" + Math.random();
  //url può essere modificato da sovrascrivendo questa funzione (portale)
  url = new Kion().getUrl(url, nameCmb);
  var formloading="#"+jQuery(nameCmb.form).attr("id")+"_loading";
  var dataType="json";
  var targetObj = document.getElementById(cmbName);
  var destType=targetObj.tagName;
  if("SELECT"!=destType.toUpperCase()) {
	  dataType="text";
  }
  jQuery(formloading).show();
  jQuery.ajax({
	  url: url,
	  success: function( data ) {
		  jQuery(formloading).hide();
		  if("SELECT"==destType.toUpperCase()) {
			  //rimuove le options
			  var comboToLoad=jQuery(targetObj);
			  jQuery("#"+cmbName+" option[value!='']").remove().end();
			  jQuery.map( data, function( item ) {
	        		var o = new Option(item.des, item.id);
	        		comboToLoad.append(o);
	                return {
	                  label: item.des,
	                  value: item.id,
	                  option: o
	                }
	              }
			  )
		  } else if("INPUT"==destType.toUpperCase() || "TEXTAREA"==destType.toUpperCase()) {
			  targetObj.value=data;
		  } else {
			  targetObj.innerHTML = data;
		  }
	 },
	  dataType: dataType,
	  error: function (jqXHR, textStatus, errorThrown) {
		  jQuery(formloading).hide();
		  alert(textStatus + '_'+errorThrown);
	  }
	});
}

/**
* Gestione dei campi nascosti alternativi 
*/
var DISABLE_ELEMENT=1;
var ENABLE_ELEMENT=2;

function hideShowElementsById() {
	var elem = document.getElementsByTagName('*');
	var inputFields, selectFields;
	for ( var i = 0; i < elem.length; i++) {
		var idAttr = elem[i].getAttribute('id');
		if ((idAttr != null) && (typeof idAttr == 'string')) {
			if (idAttr.substring(0, 5) == 'hwojs') {
				elem[i].style.display = "inline";
				inputFields = elem[i].getElementsByTagName('input');
				selectFields = elem[i].getElementsByTagName('select');
				changeDisabledAttr(inputFields, ENABLE_ELEMENT);
				changeDisabledAttr(selectFields, ENABLE_ELEMENT);
			}
			if (idAttr.substring(0, 4) == 'hwjs') {
				elem[i].style.display = 'none';
				inputFields = elem[i].getElementsByTagName('input');
				changeDisabledAttr(inputFields, DISABLE_ELEMENT);
			}
		}
	}
}

function changeDisabledAttr(elements, operation){
	  var disabled = (operation==DISABLE_ELEMENT);
	  for(var j=0;j<elements.length;j++){
	    elements[j].disabled=disabled;
	  }
}

function hideShowReliantIds(relId, show){
	var elem = document.getElementById( relId );
	if( show ){
	      elem.style.display="inline";
	}
	if( !show ){
	      elem.style.display='none';
	}
}


/* Gestione Iban */

    function alignCC(cc) {
    	retval = '';
    	for (i=cc.length; i<12; i++) {
          retval = retval + '0';
    	}
        retval = retval + cc;
        return(retval);
    }

	/**
	 * Gestione valorizzazione iban da cin abi cab ecc...
	 * @param elem form
	 * @param naziCodIban codice nazione a cui si riferisce il codice bban
	 */
    function synchIban(elem, naziCodIban) {
        var form = getForm( elem )
        
        // se scatta questo script aggiungo al form di appartenenza uno script di validazione  
        form.setAttribute('onsubmit','return checkForm(this);');

    	var iban=''
    	var cc=form.cc.value.toUpperCase();
        if (cc!='') cc = alignCC(cc);
        form.cc.value=cc;
        form.cin.value = form.cin.value.toUpperCase();
        form.abi.value = form.abi.value.toUpperCase();
        form.cab.value = form.cab.value.toUpperCase();
        form.cc.value = form.cc.value.toUpperCase();
        var bban = form.cin.value + form.abi.value + form.cab.value + cc;
        if (bban.length==23) {
        	if (naziCodIban==''){
        		iban = 'IT' + ChecksumIBAN('IT00' + bban);
        	} else {        	
        		iban = naziCodIban + ChecksumIBAN(naziCodIban+'00' + bban);        		        		
        	}
        }
    	iban += form.cin.value;
    	iban += form.abi.value;
    	iban += form.cab.value;
    	iban += cc;
        form.iban.value = iban;
		
    }
//    L'IBAN per l'Italia e' composto da 27 caratteri alfanumerici, cosi' suddivisi:
//
//        2 lettere che indicano la nazione (per l'Italia sono IT);
//        2 cifre di controllo (Cin Europeo);
//        1 lettera del Cin Italiano;
//        5 cifre dell'ABI (individua la banca);
//        5 cifre del CAB (individua l'agenzia);
//        12 cifre del conto corrente.

//    Esempio di IBAN: IT35P0300200130000003976499
//    cosi' composto: IT 35 P 03002 00130 000003976499
    
    // script che recupera il form a cui un campo appartiene 
    function getForm( genericNode ){
    	var parNode = genericNode.parentNode ; 
    	if ( parNode !=null ){
    		if ( parNode.nodeType == 1 ) { //element
        		if ( parNode.nodeName == 'FORM' ) {
	    			return parNode; 
	    		} else {
					return getForm( parNode )
	    		}
			}    	
        }
    }

    
    function synchBban( elem, naziCodIban ) {
        var form = getForm( elem )
        // se scatta questo script aggiungo al form di appartenenza uno script di validazione  
        form.setAttribute('onsubmit','return checkForm(this);');
        
		form.iban.value = form.iban.value.toUpperCase();
		
		if (naziCodIban=='') {
			naziCodIban = 'IT'
		}
	    if (form.iban.value.substring(0,2)==naziCodIban) {
	       form.cin.value = form.iban.value.substr(4,1);
	       form.abi.value = form.iban.value.substr(5,5);
	       form.cab.value = form.iban.value.substr(10,5);
	       form.cc.value  = form.iban.value.substr(15,12);
	    } else {
	       form.cin.value = '';
	       form.abi.value = '';
	       form.cab.value = '';
	       form.cc.value = '';
		}
    }
    
    function checkForm(form) {
    	//Controllo esistenza campi html
    	if (form.abi == undefined || form.abi == undefined || form.cab == undefined || form.cc == undefined) {
			return true
		}
    	var error = false;
        var msg = "OK";
        var bban = form.cin.value+form.abi.value+form.cab.value+form.cc.value;
        var iban = form.iban.value

        //form.javascript.value=1;
    	
    	if (bban.length > 0) {
           //alert('BBAN:'+bban+', '+bban.length)
           msg = BBANChk(bban);
           //alert(msg);
           error = (msg!='OK');
    	}
        if (!error && iban.length > 0) {
       //alert('IBAN:'+iban+', '+iban.length)
           msg = IBANChk(iban);
           //alert(msg);
           error = (msg!='OK');
        }
        
        if (error) alert(msg);
        if (msg!='OK') return false;
        else return true;
    }


 /* prelevati da chkIBAN.js*/
   
    
 // Modulo 97 for huge numbers given as digit strings.
    function mod97(digit_string)
    {
      var m = 0;
      for (var i = 0; i < digit_string.length; ++i)
        m = (m * 10 + parseInt(digit_string.charAt(i))) % 97;
      return m;
    }

    // Convert a capital letter into digits: A -> 10 ... Z -> 35 (ISO 13616).
    function capital2digits(ch) {
      var capitals = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
      for (var i = 0; i < capitals.length; ++i)
        if (ch == capitals.charAt(i))
          break;
      return i + 10;
    }

    // Fill the string with leading zeros until length is reached.
    function fill0(s, l)
    {
      while (s.length < l)
        s = "0" + s;
      return s;
    }

    // Calculate 2-digit checksum of an IBAN.
    function ChecksumIBAN(iban)
    {
      var code     = iban.substring(0, 2);
      var checksum = iban.substring(2, 4);
      var bban     = iban.substring(4);

      // Assemble digit string
      var digits = "";
      for (var i = 0; i < bban.length; ++i)
      {
        var ch = bban.charAt(i);
        if ("0" <= ch && ch <= "9")
          digits += ch;
        else
          digits += capital2digits(ch);
      }
      for (var i = 0; i < code.length; ++i)
      {
        var ch = code.charAt(i);
        digits += capital2digits(ch);
      }
      digits += checksum

      // Calculate checksum 
      checksum = 98 - mod97(digits);
      return fill0("" + checksum, 2);
    }

    function IBANChk(iban){
      var bban = iban.substring(4);
      var code = iban.substring(0, 2);
      var cin = iban.substring(2,4);
      var cinCalc = ChecksumIBAN(code + '00' + bban);
      //alert('Cin:'+cin+' =? '+ cinCalc);
            
      if (cin==cinCalc) return "OK";
      else return ibanMsgWrong;//"Codice IBAN non corretto";
    }    
    
 /* prelevati da chkBBAN.js */ 
    
    
 // Funzione per calcolare la somma di controllo delle posizioni dispari BBAN
    dispari = new Array(1,0,5,7,9,13,15,17,19,21,2,4,18,20,11,3,6,8,12,14,16,10,22,25,24,23)

    // Argomento: stringa BBAN da verificare
    // Restituisce "OK" se il codice è corretto e messaggio di errore se è errato
    function BBANChk(b)
    {
      // Controllo della lunghezza
      if (b.length != 23)
      {
        return(ibanBbanMsgLength); //"Controllo BBAN: La lunghezza \u00E8 diversa da 23 caratteri"
      }

      // Ciclo tra caratteri della stringa
      for (i = 0, s = 0; i < b.length; i++)
      {
        // Estrae il prossimo carattere c
        c = b.charCodeAt(i);

        // Calcola il codice k da 0 a 25
        if (48 <= c && c <= 57) // per cifra 0-9
        {
          if (i == 0)
          {
            return(ibanBbanMsgWrongCin); //"Controllo BBAN: CIN non può contenere cifre"
          }
          k = c - 48;
        }
        else if (65 <= c && c <= 90) // per lettera A-Z
        {
          if (1 <= i && i <= 10)
          {
            return(ibanBbanMsgWrongAbiCab);//"Controllo BBAN: ABI e CAB non possono contenere lettere"
          }
          k = c - 65;
        }
        else
        {
          return(ibanBbanMsgWrongFormat);//"Controllo BBAN: Sono ammesse solo cifre e lettere maiuscole"
        }

        // Calcola la somma di controllo s e il codice di controllo CIN
        if (i == 0) // codice di controllo
          kcin = k;
        else if (i % 2 == 0) // posizione pari
          s = s + k;
        else // posizione dispari
          s = s + dispari[k];
      }

      // Il resto della divisione deve coincidere con il codice di controllo
      if (s%26 != kcin)
      {
        return(ibanBbanMsgWrongCheckCode);//"Controllo BBAN: Il codice di controllo \u00E8 errato"
      }

      // Fine del controllo
      return "OK";
    }    

   /*Funzioni di gestione dell'onchange su inputText*/
    
    
    function lpad(s,len,c){
    	  c=c || '0';
    	  s=s+'';
    	  while(s.length < len) {
    		  s= c+s;
    	  }
    	  return s;
    	}
    /*funzione che restituisce un array di id dei campi callegati*/
   function getReliants(reliantsId){
    	var arrayReliants = new Array();     
    	arrayReliants = reliantsId.split(';');
    	return arrayReliants;
    }
   /*Controllo della data di partenza */
   
   var re = new RegExp("^(\\d{2})/(\\d{2})/(\\d{4})$", "");
   
   var arrMonths = new Array("Gennaio", "Febbraio", "Marzo", "Aprile",
                             "Maggio", "Giugno", "Luglio", "Agosto",
                             "Settembre", "Ottobre", "Novembre", "Dicembre");
    
   /*funzione che controlla il formato della data*/ 
   function checkDate(date)
   {
     var dt = date.match(re);
    
     if (!dt)
       {
         alert("La data va inserita nel formato gg/mm/aaaa !");
         return false ;
       }
    
     day = dt[1];
     month= dt[2];
     year = dt[3];
    
     if (month < 1 || month > 12)
       {
         alert("Specificare un mese compreso tra 1 e 12 !");
         return false;
       }
    
     // Determina il numero massimo di giorni nel mese month
     // Il calendario in uso è quello Gregoriano (introdotto da Papa Gregorio XIII nel 1582)
     // ed ha un ciclo di 400 anni con 97 anni bisestili anziché 100.
     // Il 1600 era bisestile, 1700, 1800 e 1900 no, il 2000 lo è, 2100, 2200, 2300 no etc.
     if (month == 2) maxDay = (!(year % 4) && ((year % 100) || !(year % 400))) ? 29 : 28;
     else maxDay = (month == 4 || month == 6 || month == 9 || month == 11) ? 30 : 31;
    
     if (day < 1 || day > maxDay)
       {
         alert("Il mese di " + arrMonths[month - 1] + " non ha " + day +
               " giorni\nSpecificare un giorno compreso tra 1 e " + maxDay + " !");
    
         return false;
       }
    
     return true ;
   }

    
   /*funzione che aggiunge dei giorni ad una data*/
    function addGiorniDate(el,giorni){
      var dataIn=el.value;
       	gg=dataIn.substr(0,2);
    	mm=dataIn.substr(3,2);
    	aa=dataIn.substr(6,4);
    	var startDate=new Date(aa,mm-1,gg);
    	startDate.setDate(startDate.getDate()+ parseInt(giorni));
    	var giorno=startDate.getDate();
		var mese=startDate.getMonth()+1;
		return lpad(giorno,2)+"/"+lpad(mese,2)+"/"+startDate.getFullYear();
      
    }
    
    /*funzione che aggiunge  giorni ai campi data collegati*/
    function calcoladate(el,reliantsId)
    {
    	 if (!checkDate(el.value))	
    	     {	
       		   return false;
    		 }
    	 else{
			     //array che conterrà gli id dei campi collegati con il valore da aggiungere
			    var arrayReliants = getReliants(reliantsId);
			    for(var j=0;j<arrayReliants.length;j++){
			    var arrayValori = new Array();     
			    arrayValori=arrayReliants[j].split('*'); 	  	 
			    document.getElementById(arrayValori[0]).value= addGiorniDate(el,arrayValori[1]);
			   }
    	 }
    }

/**
 * Funzione chiamata sul body onload per calcolare l'immagine di sfondo nel banner
 * Cerca nei css i selector scritta_bg<n> (vedi custom.css unipd)
 * @param sid
 */    
function randomBackgroundImageOnScritta(seed) {
	var divScritta = document.getElementById('scritta');
	var rules = findMatchingCssRule('^.scritta_bg\\d');
	var n = rules.length;
	if (n > 0) {
		x = seed.charCodeAt(0) % n + 1;
//		x=(Math.floor(Math.random()*n));
		var divScritta = document.getElementById('scritta');
		divScritta.className += ' scritta_bg' + x;
//		var ruleScritta = findMatchingCssRule('^#scritta$');
//		if (ruleScritta && ruleScritta.length > 0) {
//			ruleScritta[0].style.backgroundImage = rules[x].style.backgroundImage;
//		} 
	}
}

/**
 * Funzione che data ina regexp ritorna tutte le rules il cui selectorText fa match
 * @param regexp
 * @returns {Array}
 */
function findMatchingCssRule(regexp) {
	var matchedRules = new Array();
	var mysheets = document.styleSheets;
	var n = 0;
	for (var j = 0; j < mysheets.length; j++) {
		var rules = mysheets.item(j).cssRules ? mysheets.item(j).cssRules : mysheets.item(j).rules;
    	for (var i = 0; (rules) && (i < rules.length); i++) {
    		var selector = rules.item(i).selectorText;
    		if (selector && selector.match(regexp)) {
    			matchedRules[n] = rules.item(i);
    			n++;
    		}
    	}
	}
	return matchedRules;
}

/*	data la struttura ad albero a partire dell'id dell'oggetto, carica
 * 	lo stato dei vari nodi dell'albero e compone la visualizzazione conseguente
 * 
 * 	objectId: id dell'oggetto da espandere
 *  classToSwitch: radice del nome della classe su cui effettuare lo switch (cambio selettore per aperto/chiuso)
 *  classAnchorOpen: se vi sono 2 link di apertura/chiusura, rappresenta il nome della classe associata comune 
 */
function showTree(objectId,classToSwitch,defaultStatus, classAnchorOpen) {
	var xslTempl=document.body.getAttribute('data-xsl');
	//carica lo stato dell'albero dal session storage del browser
	var openNodes=sessionStorage.getItem(xslTempl+'_'+objectId);
	//se non c'è lo stato nel session storage, utilizza lo stato di default (passato dal chiamante)
	if(openNodes!=null) {
		var rootNodes=$('.rootNode_'+objectId);
		for(var i=0;i<rootNodes.length;i++) {
			var rootNode=rootNodes[i].id;
			showRoot(rootNode,openNodes,classToSwitch);
		}
	} else {
		sessionStorage.setItem(xslTempl+'_'+objectId,defaultStatus)
	}

}

/*
 * data una struttura richiudibile, carica lo stato
 * e compone la visualizzazione conseguente
 * 
 * 	objectId: id dell'oggetto da espandere
 *	rootId:	id del nodo	 	
 *  classToSwitch: radice del nome della classe su cui effettuare lo switch (cambio selettore per aperto/chiuso)
 *  defaultStatus: nodo aperto di default
 *  classAnchorOpen: se vi sono 2 link di apertura/chiusura, rappresenta il nome della classe associata comune 
 * 
 */
function showClosable(objectId,rootId,classToSwitch, defaultStatus, classAnchorOpen){
	var xslTempl=document.body.getAttribute('data-xsl');
	
	var openNodes=sessionStorage.getItem(xslTempl+'_'+objectId);
	if(openNodes==null) {
		openNodes=defaultStatus;
		sessionStorage.setItem(xslTempl+'_'+objectId,openNodes)
	}

	var openNodesArray = openNodes.split(",");

	rootId = rootId == null ? '' : rootId.trim();

	processDescendants(rootId,openNodesArray,true,classToSwitch,classAnchorOpen);
}

/*
 * Imposta visualizzazione nodo root (radice di un tree)
 * 
 * nodeId: id nodo root
 * openNodes: lista nodi aperti
 * classToSwitch: radice del nome della classe su cui effettuare lo switch (cambio selettore per aperto/chiuso)
 * classAnchorOpen: se vi sono 2 link di apertura/chiusura, rappresenta il nome della classe associata comune 
 */
function showRoot(nodeId,openNodes,classToSwitch, classAnchorOpen){
	var openNodesArray;
	if(openNodes!=null){
		openNodesArray = openNodes.split(",");
	} else {
		openNodesArray = new Array();
	}
	
	var open= isOpen(openNodesArray,nodeId);

	processDescendants(nodeId,openNodesArray,open,classToSwitch, classAnchorOpen);

}
/*
 * effettua l'inversione di un nodo da aperto a chiuso e viceversa
 * 
 * 	objectId: id dell'oggetto da richiudibile
 *	elemId:	id elemento da espandere o chiudere
 *  classToSwitch: radice del nome della classe su cui effettuare lo switch (cambio selettore per aperto/chiuso)
 *  classAnchorOpen: se vi sono 2 link di apertura/chiusura, rappresenta il nome della classe associata comune 
 */
function toggleElem(objectId, elemId, classToSwitch, classAnchorOpen) {
	elemId = elemId == null ? '' : elemId.trim();
	var xslTempl=document.body.getAttribute('data-xsl');
	var storedOpenNodes=sessionStorage.getItem(xslTempl+'_'+objectId);
	if(!storedOpenNodes){
		storedOpenNodes='';
	}
	storedOpenNodes=storedOpenNodes.split(",");

	var newOpenNodes= new Array();
	var openNodesToAppy= new Array();

	if(isOpen(storedOpenNodes,elemId)) {
		//nasconde nodo e figli
		for(var i=0;i<storedOpenNodes.length;i++) {
			let node = storedOpenNodes[i] == null ? '' : storedOpenNodes[i].trim();
			if (node != elemId) {
				newOpenNodes.push(node)
			}
		}
	} else {
		//apre nodo e figli già aperti
		newOpenNodes=storedOpenNodes;
		newOpenNodes.push(elemId);
	}
	openNodesToAppy=newOpenNodes;
	sessionStorage.setItem(xslTempl+'_'+objectId,newOpenNodes.toString())

	processDescendants(elemId,openNodesToAppy,true,classToSwitch, classAnchorOpen);
}

/*
 * effettua l'inversione di un nodo da aperto a chiuso e viceversa in una table con nodi richiudibili ad albero
 * 
 * 	objectId: id dell'oggetto da richiudibile
 *	elemId:	id elemento da espandere o chiudere
 *  classToSwitch: radice del nome della classe su cui effettuare lo switch (cambio selettore per aperto/chiuso)
 *  classAnchorOpen: se vi sono 2 link di apertura/chiusura, rappresenta il nome della classe associata comune
 *  reference: url di apertura/chiusura del nodo
 *  status: stato del nodo cliccato (O=Open, C=Close)
 *  paramStatus: elemento della querysting che specifica il cambio dello stato
 */
function toggleElemTree(objectId, elemId, classToSwitch, classAnchorOpen, reference,status,paramStatus) {
	var element=jQuery("#"+elemId);
	var statusOpenLocal=element.data('status-node'); //legge dal nodo se è stato caricato il contenuto
	var url;
	
	if(status=='O' || statusOpenLocal=='O') {
		var jsessionId=''
		if(reference.indexOf('jsessionid=')>0) {
			jsessionId=';'+reference.substring(reference.indexOf('jsessionid='),reference.indexOf('?'))
		}
		url=new Kion().getUrl('auth/AggiornaStatoTabClosable.do'+jsessionId+'?'+paramStatus,element);
		jQuery.get(url, function( data ) {
			var openNodesArray = data.split(",");
			processDescendants(elemId,openNodesArray,true,classToSwitch, classAnchorOpen);
		});
	} else {
		url=new Kion().getUrl(reference+'&'+paramStatus+'&FW_CP_AJAX_MODE=1',element);
		jQuery.get(url, function( data ) {
			var selElemId="#"+elemId;
			htmlIn=jQuery(jQuery.parseHTML( data ));
			htmlTab=htmlIn.filter('#'+objectId);
			if(htmlTab.length>0) {
				htmlRows=htmlIn.find(selElemId + ', .son-of-'+ elemId);
				jQuery(selElemId).replaceWith(htmlRows);
				jQuery(selElemId).data('status-node','O')
				//se è stato definita la funzione di callback la chiamo
				if(jQuery.CallBackOpenNode) {
					jQuery.CallBackOpenNode(objectId)
				}
			} else {
				//se non trova l'oggetto che si aspetta rifa la chiamata
				window.location.href=reference;
			}
		});
	}
	
}

/*
 * funzione che verifica se un elemento è contenuto in una lista
 * 
 * openNodesArray: array con i nodi su cui effettuare la ricerca
 * idElem: elemento da ricercare
 * 
 * ritorna true se elemento trovaro, false altrimenti
 * 
 */
function isOpen(openNodesArray,idElem) {
	var isOpen=false;
	if(openNodesArray) {
		for(var j=0;j<openNodesArray.length;j++) {
			if(openNodesArray[j]==idElem){
				isOpen=true;
				break;
			}
		}
	}
	return isOpen;
}

/*
 * Funzione ricorsiva che effettua la visualizzazione di un albero in base allo
 * stato di apertura dei vari nodi
 * 
 * elemId: id elemento padre
 * openNodes: lista elementi aperti
 * doShow: effettua la modifica di visualizzazione in base allo stato
 * classToSwitch: radice del nome della classe su cui effettuare lo switch (cambio selettore per aperto/chiuso)
 * classAnchorOpen: se vi sono 2 link di apertura/chiusura, rappresenta il nome della classe associata comune 
 * 
 */
function processDescendants(elemId,openNodes, doShow, classToSwitch, classAnchorOpen) {
	//trova i figli
	rowId = elemId == null ? '' : elemId.trim();
	var descendants=jQuery('.son-of-'+elemId+',.son-of-'+elemId+'-switch');
	var open=isOpen(openNodes,rowId);
	var classOpener=classToSwitch+rowId
	var classOpenerSwitch=classToSwitch+rowId+'-switch'
	var elemSwitch=jQuery('.'+classOpenerSwitch);
	//individua l'elemento di selezione apertura/chiusura (se è in stato aperto o chiuso)
	if(elemSwitch.length>0){
		//se c'è un solo elemento di switch
		var chiuso=true;
		/*
		 * se vi sono 2 elementi di switch (uno per la chiusura e uno per l'apertura), si va a verificare quale è visualizzato
		 *verificando se c'è una classe specifica che rappresenta l'apertura 
		 */
		if(classAnchorOpen) {
			//verifico se esiste l'elemento complementare di apertura/chiusura e se questo è di apertura
			if(jQuery('.'+classOpener).length>0 && elemSwitch.is('.'+classAnchorOpen)) {
				chiuso=false;
			}
		}
		/*
		 * se il nodo dev'essere aperto e attualmente è chiuso, oppure il nodo dev'essere chiuso ed
		 * attualmente è aperto, effettua lo switch
		 * 
		 */
		if(open && chiuso || !open && !chiuso){
			switchClass2(classOpener,classOpenerSwitch);
		}
	} else {
		/*
		 * non c'è nessun elemento complementare di apertura/chiusura nascosto: è sicuramente aperto
		 * se è da chiudere si effettua lo switch
		 */
		if(!open){
			switchClass2(classOpener,classOpenerSwitch);
		}
	}
	
	/*
	 * per ogni elemento figlio si verifica se è da mostrare:
	 * se nodo il padre è aperto e il flag di visualizzazione è attivo si mostra
	 * il nodo figlio, altrimenti lo si nasconde e si interrompe la ricorsione
	 */
	
	for(var i=0;i<descendants.length;i++) {
		var childId=descendants[i].id;
		if(open && doShow) {
			jQuery("#"+childId).show();
		} else {
			jQuery("#"+childId).hide();
			openNodes='';
		}
		//ricorsione sui nodi figli
		processDescendants(childId,openNodes,doShow, classToSwitch);
	}
}

/**
* Sostituisce una classe dell'elemento html con la corrispontente classe di switch.
* Es. <a href="#" class="miaclasse">mio link</a> diventa <a href="#" class="miaclasse-switch">mio link</a> 
* e viceversa, dove miaclasse e miaclasse-switch solitamente definiscono comportamenti contrapposti
*
* @param class1 classe origine
* @param class2 classe che subentra
*/
function switchClass2(class1, class2){
	var elemClasse1=jQuery('.'+class1)
	var elemClasse2=jQuery('.'+class2)
	if(elemClasse1.length>0) {
		//alert('switch classe ' + classe + ' diventa ' + classSwitch)
		elemClasse1.addClass(class2);
		elemClasse1.removeClass(class1);
	} 
	if(elemClasse2.length>0) {
		elemClasse2.addClass(class1);
		elemClasse2.removeClass(class2);
		//alert('switch classe ' + classSwitch + ' diventa ' + classe)
	}
}
/*
 * Crea un widget autocomplete ui "combobox" wrappando il select idenditificato da id
 */
function loadAutoComplete(id, isDisabled, emptyVal, lookupToLoad, numChar ) {
	(function( jQuery ) {
		jQuery.widget( "custom.combobox", {
	    	options: {
	    		emptyVal: emptyVal,
	    		isDisabled: isDisabled,
	    		lookupToLoad: lookupToLoad
	        },
	      _create: function() {
	        this.wrapper = jQuery( "<span>" )
	          .addClass( "custom-combobox" )
	          .insertAfter( this.element );
	 
	        this.element.hide();
	        this._createAutocomplete();
	        this._createShowAllButton();
	      },
	      
	      _createAutocomplete: function() {
	        var selected = this.element.children( ":selected" ), value;
	         if(selected.val()==this.options.emptyVal|| selected.length==0){
	        	value=selectionAutocompleteMsgInnerHint;
	       	 } else {
	       		 value=selected.text();
	       	 }
	        this.input = jQuery( "<input>" )
	          .appendTo( this.wrapper )
	          .val( value )
	          .attr( "title", "" )
	          .width( getAutocompleteWidth(value))
	          .addClass( "custom-combobox-input ui-widget ui-widget-content ui-state-default ui-corner-left" )
	          .autocomplete({
	            delay: 200,
	            minLength: 0,
	            source: jQuery.proxy( this, "_source" )
	          }).on('focus', function() {
	        	  this.select();
	          }).on('mouseup', function(e){
	        		e.preventDefault();
	          }).attr("title",value);
	        
	        if(this.options.isDisabled) {
	        	this.input.prop('disabled', true);
	        }
	 
	        this._on( this.input, {
	          autocompleteselect: function( event, ui ) {
	            ui.item.option.selected = true;
	            this._trigger( "select", event, {
	              item: ui.item.option
	            });
	            //chiamata evento standard del select (per loadCombo)
	            jQuery("#" + this.bindings[0].id).trigger('change');
	            //adatta la larghezza del controllo al testo selezionato
	           this.input.width(getAutocompleteWidth(ui.item.option.text,this.input.css("font-size")));
	           //setta tooltip
	           this.input.attr("title",ui.item.option.text);
	          },
	 
	          autocompletechange: "_removeIfInvalid"
	        });
	      },
	 
	      _createShowAllButton: function() {
	        var input = this.input,
	          options=this.options,
	          wasOpen = false;
	 
	        jQuery( "<a>" )
	          .attr( "tabIndex", -1 )
	          .attr( "id", this.options.id+"_open_all")
	          .tooltip()
	          .appendTo( this.wrapper )
	          .button({
	            icons: {
	              primary: "ui-icon-triangle-1-s"
	            },
	            text: false
	          })
	          .removeClass( "ui-corner-all" )
	          .addClass( "custom-combobox-toggle ui-corner-right" )
	          .on('mousedown', function() {
	        	  if(!options.isDisabled){
	        	  	wasOpen = input.autocomplete( "widget" ).is( ":visible" );
	        	  }
	          })
	          .on('click', function() {
	        	  if(!options.isDisabled){  
		            input.trigger('focus');
		            // Close if already visible
		            if ( wasOpen ) {
		              return;
		            }
		 
		            // Pass empty string as value to search for, displaying all results
		            input.autocomplete( "search", "" );
	        	  }
	          });
	      },
	 
	      _source: function( request, response ) {
	    	  if(this.options.lookupToLoad!='' && numChar>0) {
	    		  //se c'è il parametro lookupToLoad, la select viene popolata dinamicamente con il risultato della chiamata remota ajax
		    	  var select=this;
		    	  var formloading="#"+select.element.get(0).form.id+"_loading";
		    	  var showAllButton=jQuery("#" + this.options.id +"_open_all");
		    	  if(request.term.length>numChar-1) {
			    	  select.element.children( "option" ).remove().end();
			    	  jQuery(formloading).show();
			    	  jQuery.ajax({
			    		  url: this.options.lookupToLoad+request.term,
			    		  async: false,
			    		  success: function( data ) {
			    			  jQuery(formloading).hide();
			    			  response( jQuery.map( data, function( item ) {
					        		var o = new Option(item.label, item.value);
					        		select.element.append(o);
					                return {
					                  label: item.label,
					                  value: item.label,
					                  option: o
					                }
					              }
				    			  ));
			    			  if(select.element.children( "option" ).length==0){
			    				  var valNotFound= request.term + " " + selectionAutocompleteMsgInnerHint;
					    		  var o = new Option(valNotFound, "");
					    		  select.element.append(o);
					    		  response( select.element.children( "option" ).map(function() {
					    			  if(emptyVal) {
							    		  return {
							                  label: request.term + " " + selectionAutocompleteMsgNoMatch,
							                  value: emptyVal,
							                  option: o
							                }
					    			  }
					    		  }));
					    		  showAllButton.attr( "title", "");
					    	  } else {
					    		  showAllButton.attr( "title", selectionAutocompleteMsgAllItems );
					    	  }
			    		 },
			    		  dataType: "json",
			    		  error: function (jqXHR, textStatus, errorThrown) {
			    			  jQuery(formloading).hide();
			    			  alert(textStatus + '_'+errorThrown)
			    		  }
			    		});

		    	  } else {
			        response( this.element.children( "option" ).map(function() {
			          var text = jQuery( this ).text();
			          return {
			              label: text,
			              value: text,
			              option: this
			          };
			        }) );
		    	  }
	    	  } else {
	    		  	//se non c'è lookup remota, viene fatta la ricerca nelle option della select
	    		  	var matcher = new RegExp( jQuery.ui.autocomplete.escapeRegex(request.term), "i" );
		  	        response( this.element.children( "option" ).map(function() {
		  	          var text = jQuery( this ).text();
		  	          if ( this.value && ( !request.term || matcher.test(text) ) )
		  	            return {
		  	              label: text,
		  	              value: text,
		  	              option: this
		  	            };
		  	        }) );
		  	      jQuery("#" + this.options.id+"_open_all").attr( "title", selectionAutocompleteMsgAllItems );
	    	  }
	      },
	 
	      _removeIfInvalid: function( event, ui ) {
	 
	        // Selected an item, nothing to do
	        if ( ui.item ) {
	          return;
	        }
	 
	        // Search for a match (case-insensitive)
	        var value = this.input.val(),
	          valueLowerCase = value.toLowerCase(),
	          valid = false;
	        this.element.children( "option" ).each(function() {
	          if ( jQuery( this ).text().toLowerCase() === valueLowerCase ) {
	            this.selected = valid = true;
	            return false;
	          }
	        });
	 
	        // Found a match, scateno l'evento change della selection
	        if ( valid ) {
	        	jQuery("#" + this.bindings[0].id).change();
	        	return;
	        }
	 
	        // Remove invalid value
	        var selected = this.element.children( ":selected" ), // elemento correntemente selezionato
	         	oldVal = selected.text(), //testo dell'elemento correntemente selezionato
	         	val=oldVal;
	        if(value!=''){
	        	//immesso valore errato
	        	//se è selezionato il valore vuoto metto l'hint di ricerca come testo
		         if(selected.val()==this.options.emptyVal){
		        	 val=selectionAutocompleteMsgInnerHint;
		       	 }
		         //messaggio di errore all'utente
		         alert(value + " " + selectionAutocompleteMsgNoMatch);
		        this.input
		          .val( val )
		          .attr( "title", value + " " + selectionAutocompleteMsgNoMatch );
	        } else {
	        	//è stato sbiancato il campo:
	        	//cerco l'elemento vuoto
	        	var emptyOption=this.element.children( "[value='" + this.options.emptyVal +"']");
	        	//se esiste l'elemento vuoto lo setto selezionato
	        	if(emptyOption.length>0) {
	        		emptyOption.attr('selected','selected');
	        		val=selectionAutocompleteMsgInnerHint;
	        	} else {
	        		selected.removeAttr("selected");
	        		this.input.attr("required","required");
	        		this.input.attr("placeholder",selectionAutocompleteMsgInnerHint);
	        		val="";
	        	}
	        	this.input
		          .val( val )
		          .attr( "title", val);
	        }
	        this.input.data( "ui-autocomplete" ).term = "";
	        this.input.width( getAutocompleteWidth(val))
	      },
	 
	      _destroy: function() {
	        this.wrapper.remove();
	        this.element.show();
	      }
	    });
	  })( jQuery );
	
	jQuery(function() {

		jQuery( "#"+id ).combobox({id: id, emptyVal: emptyVal, isDisabled: isDisabled, lookupToLoad:lookupToLoad });
		if(jQuery( "#"+id ).children( "option" ).length>1) {
			jQuery("#" + id+"_open_all").attr( "title", selectionAutocompleteMsgAllItems );
		}

	})
}
/*
*	funzione che calcola la larghezza del contollo autocomplete con limite massimo
*/
function getAutocompleteWidth(text,font) {
	var _width=text.width(font);
	if(_width>425){
		_width=425;
	}
	if(text.length>0 && _width<100){
		_width=100;
	}
	if(text.length==0) {
		_width=selectionAutocompleteMsgInnerHint.width(font)
	}
	return _width;
}
/*
 * calcola larghezza di un testo su schermo con un particolare font
 */
String.prototype.width = function(font) {
  var f = font || '1em arial',
      o = $('<div>' + this + '</div>')
            .css({'position': 'absolute', 'float': 'left', 'white-space': 'nowrap', 'visibility': 'hidden', 'font': f})
            .appendTo($('body')),
      w = o.width();

  o.remove();

  return w;
}

/*
 * Metodo utilizzato per fare il preview delle immagini caricate tramite from
 * Vedi template inputText con parametro contentType='F' e previewImgId valorizzato con id del tag img
 */
function previewInputFileImg(input, previewImgId) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        var jqueryId = '#' + previewImgId;
        reader.onload = function (e) {
            $(jqueryId)
                .attr('src', e.target.result);
        };

        reader.readAsDataURL(input.files[0]);
    }
}

/**
* Funzione che permette di controllare che la form sia inviata una volta sola.
* Deve essere invocata nell'evento onSubmit delle form con la seguente sintassi:
* ... onSubmit="return checkFormSingleSubmit(this);" ...
*/
var submittedForm = null;
function checkFormSingleSubmit(form) {
	if (submittedForm!=form) {
		submittedForm = form;
		return true;
	} else {
		alert(actionbarMultipleSubmit);
		return false;
	}
}

/**
* Funzione che aggiunge o rimuove un elemento da un array di elementi selezionati (advanced table)
* @param id id da gestire
* @param idSelected booleano che indica se l'id è selezionato (true) o deselezionato (false)
* @param idsOfSelectedRows array contenete gli id selezionati 
* 
*/
function updateIdsOfSelectedRows(id, isSelected,idsOfSelectedRows) {
    var index = jQuery.inArray(id, idsOfSelectedRows);
    if (!isSelected && index >= 0) {
        idsOfSelectedRows.splice(index, 1); // remove id from the list
    } else if (index < 0 && isSelected) {
        idsOfSelectedRows.push(id);
    }
};
//funzioni di gestione persistenza filtri in jqgrid (table advanced=2)
/**
* Funzione che ripristina i filtri di ricerca della tabella con jqgrid, pagina selezionata e ordinamenti
* @param $grid riferimento alla grid
* @param myDefaultSearch tipo di ricerca impostato 
*/
function refreshSerchingToolbar($grid, myDefaultSearch) {
    var p = $grid.jqGrid("getGridParam"), postData = p.postData, filters, i, l,
        rules, rule, iCol, cm = p.colModel,
        cmi, control, tagName;

    for (i = 0, l = cm.length; i < l; i++) {
        control = jQuery("#gs_" + jQuery.jgrid.jqID(cm[i].name));
        if (control.length > 0) {
            tagName = control[0].tagName.toUpperCase();
            if (tagName === "SELECT") { // cmi.stype === "select"
                control.find("option[value='']")
                    .attr("selected", "selected");
            } else if (tagName === "INPUT") {
                control.val("");
            }
        }
    }
    if (typeof (postData.filters) === "string" &&
            typeof ($grid[0].ftoolbar) === "boolean" && $grid[0].ftoolbar) {

        filters = JSON.parse(postData.filters);
        if (filters && filters.groupOp === "AND" && 
        	filters.groups === undefined) {
            // only in case of advance searching without grouping we import filters in the
            // searching toolbar
            rules = filters.rules;
            for (i = 0, l = rules.length; i < l; i++) {
                rule = rules[i];
                iCol = p.iColByName[rule.field];
                if (iCol >= 0) {
                    cmi = cm[iCol];
                    control = jQuery("#gs_" + jQuery.jgrid.jqID(cmi.name));
                    if (control.length < 0 &&
                            (((cmi.searchoptions === undefined ||
                            cmi.searchoptions.sopt === undefined)
                            && rule.op === myDefaultSearch) ||
                              (typeof (cmi.searchoptions) === "object" &&
                            		  jQuery.isArray(cmi.searchoptions.sopt) &&
                                  cmi.searchoptions.sopt.length > 0 &&
                                  cmi.searchoptions.sopt[0] === rule.op))) {
                        tagName = control[0].tagName.toUpperCase();
                        alert(tagName)
                        if (tagName === "SELECT") { // && cmi.stype === "select"
                            control.find("option[value='" + jQuery.jgrid.jqID(rule.data) + "']")
                                .attr("selected", "selected");
                        } else if (tagName === "INPUT") {
                            control.val(rule.data);
                        }
                    }
                }
            }
        }
        $grid.jqGrid('setGridParam', {page: $grid.jqGrid('getGridParam','page')}).trigger("reloadGrid");
    }
};

/**
* Funzione che salva un oggetto nel local storage del browser
* @param storageItemName node variabile dello storage da salvare
* @param object oggetto da salvare
*/
function saveObjectInLocalStorage(storageItemName, object) {
    if (window.localStorage !== undefined) {
        window.localStorage.setItem(storageItemName, JSON.stringify(object));
    }
};

/**
* Funzione che rimuove un oggetto nel local storage del browser
* @param storageItemName variabile dello storage da eliminare
*/
function removeObjectFromLocalStorage(storageItemName) {
    if (window.localStorage !== undefined) {
        window.localStorage.removeItem(storageItemName);
    }
};

/**
* Funzione che recupera un oggetto nel local storage del browser
* @param storageItemName variabile dello storage da recuperare
*/
function getObjectFromLocalStorage(storageItemName) {
    if (window.localStorage !== undefined) {
        return JSON.parse(window.localStorage.getItem(storageItemName));
    }
};

/**
* Funzione che genera il nome della variabile in cui salvare lo stato della grid (univoco: path_pagina#id_grid)
* @param grid jqgrid
*/
function myColumnStateName(grid) {
    return window.location.pathname + "#" + grid[0].id;
};
/**
* Funzione che recupera l'array dei nomi delle colonne della jqGrid
*/
function getColumnNamesFromColModel() {
    var colModel = this.jqGrid("getGridParam", "colModel");
    return jQuery.map(colModel, function (cm, iCol) {
        // we remove "rn", "cb", "subgrid" columns to hold the column information 
        // independent from other jqGrid parameters
        return jQuery.inArray(cm.name, ["rn", "cb", "subgrid"]) >= 0 ? null : cm.name;
    });
};

/**
* Funzione che salva lo stato delle colonne
*/
function saveColumnState() {
    var p = this.jqGrid("getGridParam"), colModel = p.colModel, i, l = colModel.length, colItem, cmName,
        postData = p.postData,
        columnsState = {
            search: p.search,
            page: p.page,
            rowNum: p.rowNum,
            sortname: p.sortname,
            sortorder: p.sortorder,
            cmOrder: getColumnNamesFromColModel.call(this),
            colStates: {}
        },
        colStates = columnsState.colStates;

    if (postData.filters !== undefined) {
        columnsState.filters = postData.filters;
    }

    for (i = 0; i < l; i++) {
        colItem = colModel[i];
        cmName = colItem.name;
        if (cmName !== "rn" && cmName !== "cb" && cmName !== "subgrid") {
            colStates[cmName] = {
                width: colItem.width,
                hidden: colItem.hidden
            };
        }
    }
    saveObjectInLocalStorage(myColumnStateName(this), columnsState);
};

/**
* Funzione che ripristina lo stato delle colonne(filtri, ordinamenti) dal local storage
* @param colModel oggetto modello colonne
*/
function restoreColumnState(colModel) {
	    var colItem, i, l = colModel.length, colStates, cmName,
	    columnsState = getObjectFromLocalStorage(myColumnStateName(this));
	
	if (columnsState) {
	    colStates = columnsState.colStates;
	    for (i = 0; i < l; i++) {
	        colItem = colModel[i];
	        cmName = colItem.name;
	        if (cmName !== "rn" && cmName !== "cb" && cmName !== "subgrid") {
	            colModel[i] = jQuery.extend(true, {}, colModel[i], colStates[cmName]);
	        }
	    }
	}
	return columnsState;
};

/**
* Funzione che gestisce la selezione degli items sulle tabelle advanced
* @param arraySelected array id righe selezionate
* @param varSelAll flag selezione di tutte le righe
* @param rowid id riga selezionata
* @param isSelected stato della riga selezionata (selezionata/deselezionata)
*/
function tableSelect(arraySelected, rowid, isSelected) {
	updateIdsOfSelectedRows(rowid, isSelected, arraySelected);
	return false;
	
};

/**
* Funzione che gestisce la selezione di tutti gli items sulle tabelle advanced
* @param arraySelected array id righe selezionate
* @param varSelAll flag selezione di tutte le righe
* @param arrayAllRows array con tutte le righe dalla table
* @param isSelected stato della riga selezionata (selezionata/deselezionata)
*/
function tableSelectAll(arraySelected, arrayAllRows, isSelected) {
	arraySelected.length=0;
    if(isSelected) {
    	arraySelected.push.apply(arraySelected, arrayAllRows);
    	return true;
    } else {
    	return false;
    }
}

/**
* Funzione che gestisce la selezione/deselezione di tutti le righe visibili sulle tabelle advanced 2
* @param tableId id della tabella su cui selezionare i campi
* @param selectionName nome dei campi checkbox in tabella
*/
function tableSelectAllVisible(tableId, selectionName) {
	$("#" + tableId + " input[name='_" + selectionName + "']").click();
}

var Kion = function() {};

Kion.prototype.getUrl = function(pUrl, pReferredElement) {
    var url = pUrl;
    return url;
}
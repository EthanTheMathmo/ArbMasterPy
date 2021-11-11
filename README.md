# ArbMasterPy

Master sheet for inventory management and arbitrage on Amazon


# TO-DO

Update of TO-DO 11.11.21
We have now implemented basic automated arbitrage price searching, which is in use. This is the main focus. Things to implement are:
1. server implementation (not local)
2. queuing tasks
3. multiple providers for speed gain?


17.10.21
All implemented other than the (1) explanations thing. That needs some thought
other than that:
TO-DO: work out the mac specific deployment bug probably involving the decorators and multiprocess

15.10.21
call w./ james today. He has recovered from his bout of flu
1. Explanations for how to use things properly 'I'm not sure if I was making a mistake...'
2. re-ordering/shipment layout
3. shipment data example now sent to us - need to implement
4. fixing SKU bug

10.10.21-12.10.21
We deployed updates successfully this sunday. James has a list of 6 features/improvements he thinks would improve the product, and is next free on wednesday to update
these are:
1. Build automatic amazon shipping export into the master sheet
2. Improve aesthetics of master sheet (although - he'd try some stuff out and send back to us on this)
3. Improve layout of ribbon buttons. (in particular, buttons which are only meant to be used on the master sheet in one place, and buttons which can be used elsewhere go elsewhere)
4. Speed of import col needs to be imrpoved to match the other functions
5. For shipping sheet, make sure there's a way to only select certain SKUs, as provided by his shipping centre
6. collapsing rows by month, so they remain in the master sheet but dont use unnecessary space

9.10.21
1. redeploy to james' machine the updates
2. easy access to ASIN data and import


8.10.21
1. Finish remaining inventory changes suggested by James (key one implemented, one mroe to do)
2. Freeze bug when cancel is clicked. 
3. Implement speed imrpovements and GUI improvements. 

7.10.21
1. Implement inventory sheet as suggested by James. (only upload asins if not in sheet). 
2. (maybe) Check for empty rows in inventory sheet, as this would screw up 
3. Fix bug where clicking cancel freezes the code. 
4. fix keep_on_top=True not working on mac. 
5. Make wording for import data clearer (not sure how to best do this one)

and then (6) deploy these changes as update to james



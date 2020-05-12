/*
*  Created by: Anhtien Nguyen
*  Date:  June 11, 2018
*  Description:  an electrical box with the dimension
*/

/* By: Ye Zhang (mr.yezhang@gmail.com)
   Date: May 9, 2020
    Added screw tab out of box; removed box bottom screw holes, which are blocked after outlet is installed; Removed two supporting cylinders; Refactored code to imporve maintainability etc. 
   Date: May 10, 2020
    Remove two holes from cover.
    Enlarge screw holes.
    Fine tune screw hole distance. 
    Reduce box bottom tab thickness.
    Moved screw holes on bottom tab further from box wall. Give more work space. 
*/

// Choose, which part you want to see!
part = "all_parts__";  //[all_parts__:All Parts,bottom_part__:Bottom,top_part__:Top]

// Standard width is 69.33mm. This is inner space width.
width=52; //[51:85]
// Inner space height. Default 41mm
height=41;  // [37:70]

// Wall thickness in mm, add to width and height. Actuall wall (including cover) thickness is
// half of this value. 
wall_double_thickness=3.5; // [1:4]
// outlet screw diameter (mm) for the holes at 2 ends
outlet_screw_hole_diag=3.4; // [3:6]
// the screw hole on box bottom tab, to secure the box.
bottom_tab_screw_hole_diag=5;
// width of hole to run the input wires (mm)
// This 14/2 wire width is 10, height is 5
wires_hole_width=11; // [8:12]
// height of hole to run the input wires (mm)
wires_hole_height=6; // [4:12]
// https://smile.amazon.com/gp/product/B000BPEQCC/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1

// Program Section //
if(part == "bottom_part__") {
    box();
} else if(part == "top_part__") {
    cover();
} else if(part == "all_parts__") {
    all_parts();
} else {
    all_parts();
}

module all_parts() {
translate([0, 0, (height+wall_double_thickness/2)/2]) 
    box();

 // this put cover next to box
 translate([width+(wall_double_thickness*2), 0, wall_double_thickness/4 /*wall_double_thickness/2/2 puts the cover touch build surface*/])  
 // this displacement puts the cover on top
 // translate([0,0,(height+wall_double_thickness/2)+1])
    cover();
}

// Inner space length.
length=106; // Note: if you change this, you must update screw_posistion_from_edge accordingly.
outlet_screw_hole_depth=35; // how far down is the outlet screw hole in supporting cylinder.
support_cylinder_radius=outlet_screw_hole_diag*2+1;

// distance between supporting cylinder and box top
cylinder_top_gap=5.5-wall_double_thickness; // deduct cover thickness so the outlet will be flush.

// outlet screw off set from edge. Change according to your measurement with caution!
// My desin references x,y,z 0 (center), and thus changing wall thickness won't inerference screw_position.
screw_posistion_from_edge=11; // Outlet screw holes are 84mm apart. Must be precise!

module one_plug_hole() {
    difference(){
        cylinder(r=17.4625, h=15, center = true, $fn=50);
        translate([-24.2875,-15,-2]) cube([10,37,15], center = false);
        translate([14.2875,-15,-2]) cube([10,37,15], center = false);
   }
}

module cover(width=width, length=length, height=height, screw_pos=screw_posistion_from_edge) {
    difference() {
        // define plate
        cube([width + wall_double_thickness, length + wall_double_thickness, wall_double_thickness/2], center=true);

        rotate([0,0,90]) 
            translate([-length/2+11.5, 0, 0]) // why is this magic number?
                union() {
                    translate([height+19.3915, 0, 0]) 
                    {
                        one_plug_hole();
                    }
                
                    translate([height-19.3915, 0, 0]){
                        one_plug_hole();
                    }
                    
                    // center hole. 4mm diameter.
                    // printed holes tend to shrink, give it 5mm. 
                    translate([height, 0, -3]) cylinder(r=2.5, h=20, $fn=50); 
                    translate([height, 0, 3.5]) cylinder(r1=2.5, r2=3.3, h=3);            
                }

        /*
        // define holes at 2 ends
        translate([0, -length/2 + screw_pos, -wall_double_thickness]) 
            // make screw cross cover hole easy by adding 0.2
            cylinder(r=outlet_screw_hole_diag/2 + 0.2, h=wall_double_thickness*2,$fn=60);
        translate([0, length/2-screw_pos,-wall_double_thickness]) 
            // make screw cross cover hole easy by adding 0.2
            cylinder(r=outlet_screw_hole_diag/2 + 0.2, h=wall_double_thickness*2,$fn=60); */
    }
}


module box_walls(ow_width, ow_length, ow_height) {
        difference() {
            // box walls
            difference() {
                // outside wall
                cube([ow_width, ow_length, ow_height],center=true);
                // inside wall
                translate([0, 0, wall_double_thickness/2]) 
                    cube([width, length, height], center=true);
            } 
        
        // input wires hole on side wall
       translate([ow_width/2, -(ow_length/4), -ow_height/4])
            // cube's x, y, z parameters confirm to the overall axes, making reasoning simple. 
            cube([wall_double_thickness*2, wires_hole_width, wires_hole_height], center=true);
    }
}

module outlet_screw_cylinder(length, ow_height, screw_pos) {
    cylinder_height = ow_height - cylinder_top_gap;

    translate([0, -length/2, -ow_height/2])
        difference(){
                // the support cylinder
                scale([1, 2.1, 1]) 
                    cylinder(h=cylinder_height, 
                            r1=support_cylinder_radius, 
                            r2=support_cylinder_radius, $fn=60, center=false);
                
                translate([0, -support_cylinder_radius*1.5, ow_height/2+wall_double_thickness]) // to make tab strong, its thickness equals to wall_double_thickness
                 {
                    scale([1, 1.5, 1])
                        // remove half of the outer cylinder                  
                        cube([support_cylinder_radius*2, support_cylinder_radius*2, 
                              ow_height], true);
                    // screw hole in the outside cylinder tab
                    translate([0, 2, -3])
                        cylinder(r=bottom_tab_screw_hole_diag/2, h=ow_height*2, $fn=50, center=true);
                }
                    
                // screw hole in the cylinder
                translate([0, screw_pos, cylinder_height-outlet_screw_hole_depth+1]) {
                        cylinder(r=outlet_screw_hole_diag/2, h=outlet_screw_hole_depth, $fn=50, center=false);
            }
        }
}

module lengh_support(ow_width, ow_height, wall_double_thickness) {
    rotate([0,0,90]) 
        translate([0, -(ow_width/2)+wall_double_thickness/2, -ow_height/2])
            scale([1, 0.6, 1]) // support_cylinder_radius shrink widthwise, leave more room for outlet body.
                difference(){
                    cylinder(ow_height, support_cylinder_radius, support_cylinder_radius, $fn=60);
                    translate([-support_cylinder_radius, -support_cylinder_radius*2-1, -1])
                        cube([support_cylinder_radius*2, support_cylinder_radius*2, ow_height+wall_double_thickness]);
                }
}

/*
 * Function box()
 * Draw the box 
 */
module box(width=width, length=length, height=height, screw_pos=screw_posistion_from_edge) {
    ow_width = width+wall_double_thickness;
    ow_length = length+wall_double_thickness;
    ow_height = height+wall_double_thickness/2;
   
    box_walls(ow_width, ow_length, ow_height);
      
    // outlet screw cylinder
    outlet_screw_cylinder(length, ow_height, screw_pos);
    // the other one
    rotate([0,0,180])  
        outlet_screw_cylinder(length, ow_height, screw_pos);
    
    // support lengh-wide
    lengh_support(ow_width, ow_height, wall_double_thickness);
    
    
    // the other support lengh-wide
    rotate([0,0,180]) 
        lengh_support(ow_width, ow_height, wall_double_thickness);
}
import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';
import {FormsModule} from '@angular/forms'; // <-- NgModel lives here
import {FlexLayoutModule} from '@angular/flex-layout';
import {AppComponent} from './app.component';
import {ScenarioComponent} from './scenario/scenario.component';
import {HttpClientModule} from '@angular/common/http';
import {ModalityComponent} from './modality/modality.component';
import {CommonModule} from "@angular/common";
import {NgxSliderModule} from '@angular-slider/ngx-slider';
// Testing
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {MatExpansionModule} from '@angular/material/expansion';
import {MatInputModule} from '@angular/material/input';
import {MatSidenavModule} from '@angular/material/sidenav';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatSelectModule} from '@angular/material/select';
import {MatButtonModule} from '@angular/material/button';
import {MatIconModule} from '@angular/material/icon';
import {CarouselComponent} from "./carousel/carousel.component";
import {EditorComponent} from './editor/editor.component';
import {TokenContainerComponent} from './token-container/token-container.component';
import {SegmentDirective} from './segment/segment.directive';
import {SegmentEditorComponent} from './segment-editor/segment-editor.component';
import {SegmentsTimeComponent} from './segments-time/segments-time.component';
import {SegmentsBoundingboxComponent} from "./segments-boundingbox/segments-boundingbox.component";
import {SegmentsOffsetComponent} from "./segments-offset/segments-offset.component";
import {AnnotationEditorComponent} from "./annotation-editor/annotation-editor.component";
import {AnnotationDirective} from "./annotation/annotation.directive";
import {AnnotationsDisplayComponent} from "./annotations-display/annotations-display.component";
import {ContainerViewComponent} from "./container-view/container-view.component";
import {ContainerDirective} from "./container/container.directive";
import {ContainersImgComponent} from "./containers-img/containers-img.component";
import {ContainersTextComponent} from "./containers-text/containers-text.component";
import {SegmentsAtomicComponent} from "./segments-atomic/segments-atomic.component";
import {AnnotationsPersonComponent} from './annotations-person/annotations-person.component';
import {AnnotationsObjectComponent} from './annotations-object/annotations-object.component';
import {AnnotationsEmotionComponent} from './annotations-emotion/annotations-emotion.component';
import {AnnotationsGenericComponent} from './annotations-generic/annotations-generic.component';
import {AnnotationsPosComponent} from './annotations-pos/annotations-pos.component';
import {AnnotationsTokenComponent} from './annotations-token/annotations-token.component';
import {AnnotationsTripleComponent} from './annotations-triple/annotations-triple.component';

// import { AppRoutingModule } from './app-routing.module';


@NgModule({
  declarations: [
    AppComponent,
    ScenarioComponent,
    ModalityComponent,
    CarouselComponent,
    EditorComponent,
    ContainersImgComponent,
    ContainersTextComponent,
    TokenContainerComponent,
    AnnotationDirective,
    AnnotationEditorComponent,
    AnnotationsDisplayComponent,
    ContainerDirective,
    ContainerViewComponent,
    SegmentDirective,
    SegmentEditorComponent,
    SegmentsAtomicComponent,
    SegmentsBoundingboxComponent,
    SegmentsOffsetComponent,
    SegmentsTimeComponent,
    AnnotationsPersonComponent,
    AnnotationsObjectComponent,
    AnnotationsEmotionComponent,
    AnnotationsPosComponent,
    AnnotationsTokenComponent,
    AnnotationsTripleComponent,
    AnnotationsGenericComponent
  ],
  imports: [
    CommonModule,
    BrowserModule,
    BrowserAnimationsModule,
    MatButtonModule,
    MatExpansionModule,
    MatInputModule,
    MatIconModule,
    MatSidenavModule,
    MatSelectModule,
    MatFormFieldModule,
    FlexLayoutModule,
    FormsModule,
    HttpClientModule,
    // AppRoutingModule,
    NgxSliderModule,


    // The HttpClientInMemoryWebApiModule module intercepts HTTP requests
    // and returns simulated server responses.
    // Remove it when a real server is ready to receive requests.
    // HttpClientInMemoryWebApiModule.forRoot(
    //   InMemoryDataService, { dataEncapsulation: false }
    // ),
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }

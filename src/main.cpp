#include <iostream>
#define SOKOL_IMPL
#define SOKOL_GLCORE
#include "sokol_gfx.h"
#include "sokol_app.h"
#include "sokol_log.h"
#include "sokol_glue.h"

/// SHADER
#include <triangle-sapp.glsl430.h>

// application state
static struct {
    sg_pipeline pip;
    sg_bindings bind;
    sg_pass_action pass_action;
} state;

void init_cb() {
    sg_desc desc{
        .environment = sglue_environment(),
        .logger.func = slog_func,
    };

    sg_setup(&desc);

    // a vertex buffer with 3 vertices
    float vertices[] = {
        // positions            // colors
         0.0f,  0.5f, 0.5f,     1.0f, 0.0f, 0.0f, 1.0f,
         0.5f, -0.5f, 0.5f,     0.0f, 1.0f, 0.0f, 1.0f,
        -0.5f, -0.5f, 0.5f,     0.0f, 0.0f, 1.0f, 1.0f
    };

    sg_buffer_desc buffer_desc{
        .data = SG_RANGE(vertices),
        .label = "triangle-vertices"
    };

    state.bind.vertex_buffers[0] = sg_make_buffer(&buffer_desc);

    // create shader from code-generated sg_shader_desc
    sg_shader shd = sg_make_shader(triangle_shader_desc(sg_query_backend()));

    sg_pipeline_desc pipeline_desc{
        .shader = shd,
        // if the vertex layout doesn't have gaps, don't need to provide strides and offsets
        .layout = {
            .attrs = {
                [ATTR_triangle_position].format = SG_VERTEXFORMAT_FLOAT3,
                [ATTR_triangle_color0].format = SG_VERTEXFORMAT_FLOAT4
            }
        },
        .label = "triangle-pipeline"
    };

    // create a pipeline object (default render states are fine for triangle)
    state.pip = sg_make_pipeline(&pipeline_desc);

    // a pass action to clear framebuffer to black
    state.pass_action = (sg_pass_action) {
        .colors[0] = { .load_action=SG_LOADACTION_CLEAR, .clear_value={0.0f, 0.0f, 0.0f, 1.0f } }
    };
}

void frame_cb() {
    sg_pass pass{ .action = state.pass_action, .swapchain = sglue_swapchain() };
    sg_begin_pass(&pass);
    sg_apply_pipeline(state.pip);
    sg_apply_bindings(&state.bind);
    sg_draw(0, 3, 1);
    sg_end_pass();
    sg_commit();
}

void cleanup_cb() {
    sg_shutdown();
}

void event_cb(const sapp_event *event) {}

sapp_desc sokol_main(int argc, char* argv[]) {
    return (sapp_desc) {
        .init_cb = init_cb,
        .frame_cb = frame_cb,
        .cleanup_cb = cleanup_cb,
        .event_cb = event_cb,
        .width = 640,
        .height = 480,
        .logger = sapp_logger {
            .func = slog_func
        }
    };
}

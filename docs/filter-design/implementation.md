# 4.2 Real-time implementation

As we saw [earlier](approaches.md), the single pole IIR yields a HPF with desirable performance. We will therefore replace the simple HPF we implemented for the alien voice effect with such a filter. Moreover, we will implement a [_biquad filter_](https://en.wikipedia.org/wiki/Digital_biquad_filter), which is a second order \(two pole and two zeros\) IIR filter; the biquad is one of the most-used filters.

The above Wikipedia article provides a great overview of the different ways a biquad filter can be implemented, _without code however_. We will guide you through the Python implementation of two approaches: Direct Form 1 and Direct Form 2. With these implementations in hand, it should be straightforward to port the code to C. As we did with the alien voice effect, we will implement the HPF in Python as close as possible as would be done in C.

## Direct Form 1

This is considered the more straightforward implementation, as it follows the standard formulation of the difference equation:

$$
y[n] = b_0 x[n] + b_1 x[n-1] + b_2 x[n-2] - a_1 y[n-1] - a_2 y[n-2].
$$

The corresponding block diagram is shown below.

![](../.gitbook/assets/biquad_direct_1_wiki-1%20%281%29.png)

_Figure: Block diagram of biquad, Direct Form 1._ [Source](https://en.wikipedia.org/wiki/Digital_biquad_filter#/media/File:Biquad_filter_DF-I.svg).

From the block diagram, we can essentially "read-off" the operations that need to be performed in our code. Below, we show the _**incomplete**_ `process` function, which is provided to you in [this script](https://github.com/LCAV/dsp-labs/blob/master/scripts/filter_design/biquad_direct_form_1_incomplete.py) in the repo. The complete `init` function, which sets the filter coefficients and allocates memory for the state variables, is provided to you.

```python
def process(input_buffer, output_buffer, buffer_len):

    # specify global variables modified here
    global y, x

    # process one sample at a time
    for n in range(buffer_len):

        # apply input gain
        x[0] = int(GAIN * input_buffer[n])

        # compute filter output
        output_buffer[n] = int(b_coef[0] * x[0] / HALF_MAX_VAL)
        for i in range(1, N_COEF):
            # TODO: add prev input and output according to block diagram
            output_buffer[n] += 0

        # update state variables
        y[0] = output_buffer[n]
        for i in reversed(range(1, N_COEF)):
            # TODO: shift prev values
            x[i] = 0
            y[i] = 0
```

Note the variable `HALF_MAX_VAL` in order to use the full range of the signal's data type.

The line:

```python
output_buffer[n] = int(b_coef[0] * x[0] / HALF_MAX_VAL)
```

computes the contribution of the top branch \(in the above block diagram\) towards the output $$y[n]$$.

{% hint style="info" %}
TASK 2: In the `for` dedicated to computing the filter output, determine the code in order to add the contribution from the remaining branches. This should include a previous input _and_ output sample weighted by the appropriate coefficients.

_Hint: remember to use `HALF_MAX_VAL` and to cast to `int.`_
{% endhint %}

Note that we write a `for` in order to accommodate filters with more than two poles/zeros without changing the code. However, due to stability issues it may be better to cascade multiple biquads instead of creating a filter with more than two poles/zeros.

{% hint style="info" %}
TASK 3: In the final `for` loop, update the state variables, that is the previous input and output sample values.
{% endhint %}

Running the incomplete script will yield the following plot, in which only a gain \(less than one\) is applied to the input signal.

![](../.gitbook/assets/direct_form_1_incomplete-1%20%282%29.png)

If you successfully complete the `process` function, you should obtain the following plot.

![](../.gitbook/assets/direct_form_1_complete%20%281%29.png)

## Direct Form 2

The second implementation we will consider is known as Direct Form 2. It uses less memory for state variables by placing the feedback portion first. [This article](http://www.earlevel.com/main/2003/02/28/biquads/) provides a nice visual of how to get from Direct Form 1 to Direct Form 2.

The difference equation for Direct Form 2 is given by:

$$
y[n] = b_0 w[n] + b_1 w[n-1] + b_2 w[n-2],
$$

where:

$$
w[n] = x[n] - a_1 w[n-1] - a_2 w[n-2].
$$

The corresponding block diagram is shown below.

![](../.gitbook/assets/biquad_direct_2_wiki-1%20%281%29.png)

_Figure: Block diagram of biquad, Direct Form 2._ [Source](https://en.wikipedia.org/wiki/Digital_biquad_filter#/media/File:Biquad_filter_DF-II.svg).

As before, we provide an _**incomplete**_ `process` function, which can be found in [this script](https://github.com/LCAV/dsp-labs/blob/master/scripts/filter_design/biquad_direct_form_2_incomplete.py) in the repo. The complete `init` function, which sets the filter coefficients and allocates memory for the state variables, is provided to you.

```python
def process(input_buffer, output_buffer, buffer_len):

    # specify global variables modified here
    global w

    # process one sample at a time
    for n in range(buffer_len):

        # apply input gain
        w[0] = int(GAIN * input_buffer[n])

        # compute contribution from state variables
        for i in range(1, N_COEF):
            # TODO: accumulate signal at top-left adder using prev `w` (middle column)
            w[0] -= 0

        # compute output
        output_buffer[n] = 0
        for i in range(N_COEF):
            # TODO: accumulate signal at top-right adder using `w`
            output_buffer[n] += 0

        # update state variables
        for i in reversed(range(1, N_COEF)):
            # TODO: shift prev values
            w[i] = 0
```

The first step is to compute:

$$
w[n] = x[n] - a_1 w[n-1] - a_2 w[n-2].
$$

{% hint style="info" %}
TASK 4: Complete the first \(inner\) `for` loop in order to update the value of `w[0]` \(which corresponds to w\[n\] in the above difference equation\). You should use the previous values `w[1:]` \(w\[n-1\], w\[n-2\], ...\) and `a_coeff`.

_Hint: remember to use `HALF_MAX_VAL` and to cast to `int`._
{% endhint %}

Then we can compute the output:

$$
y[n] = b_0 w[n] + b_1 w[n-1] + b_2 w[n-2].
$$

{% hint style="info" %}
TASK 5: Complete the next \(inner\) `for` loop in order to set the output sample of `output_buffer[n]`, using `w` and `b_coeff`.

_Hint: remember to use `HALF_MAX_VAL` and to cast to `int`._
{% endhint %}

Finally, we need to update the state variables for computing the next sample.

{% hint style="info" %}
TASK 6: Complete the final `for` loop in order to update the values of `w`.
{% endhint %}

Running the incomplete script will yield the following plot, where the output is all-zeros.

![](../.gitbook/assets/direct_form_2_incomplete-1.png)

If you successfully complete the `process` function, you should obtain the following plot.

![](../.gitbook/assets/direct_form_2_complete%20%281%29.png)

## C implementation

With the above implementation\(s\) working in the simulated environments with a fixed WAV file, you can now try your implementation in a real-time scenario.

There we give you the variable initialisation that you could use:

```c
#define num_coefs 3

int16_t coefs_b[] = { half_MAX_INT16, -2*half_MAX_INT16, half_MAX_INT16};
int16_t coefs_a[] = { 0*half_MAX_INT16, 1.96*half_MAX_INT16, -0.9604*half_MAX_INT16};

int16_t x_old[num_coefs] = {0, 0, 0};
int16_t y_old[num_coefs] = {0, 0, 0};
int16_t ix = 0;
int16_t iy = 0;
```

{% hint style="info" %}
TASK 7: Try your biquad filter implementation with the [`sounddevice` template](https://github.com/LCAV/dsp-labs/blob/master/scripts/_templates/rt_sounddevice.py) and then implement it in C on the microcontroller!

_Hint: for the C implementation, start off with the passthrough example._
{% endhint %}

**Congrats on implementing the biquad filter! This is a fundamental tool in the arsenal of a DSP engineer. In the** [**next chapter**](../granular-synthesis/)**, we will build a more sophisticated voice effect that can alter the pitch so that you sound like a chipmunk or Darth Vader.**

## Tasks solutions

{% tabs %}
{% tab title="Anti-spoiler tab" %}
Are you sure you are ready to see the solution? ;\)
{% endtab %}

{% tab title="Task 2" %}
You need to implement the filter as presented in the figure for the direct form. To do this you need to use the coeficients _a\_coef\[i\]_, _b\_coef\[i\]_ and the input and output _x\[i\]_ and _y\[i\]._ As always in the micro-controller environment, you have to be careful to respect the variable type, range, and to scale down your variables as needed for example with the look-up table. The result is shown in line 15 below.

\_\_

```python
# the process function!
def process(input_buffer, output_buffer, buffer_len):
    # specify global variables modified here
    global y, x

    # process one sample at a time
    for n in range(buffer_len):

        # apply input gain
        x[0] = int(GAIN * input_buffer[n])

        # compute filter output
        output_buffer[n] = int(b_coef[0] * x[0] / HALF_MAX_VAL)
        for i in range(1, N_COEF):

            output_buffer[n] += int((b_coef[i] * x[i] / HALF_MAX_VAL) - (a_coef[i] * y[i] / HALF_MAX_VAL))
```
{% endtab %}

{% tab title="Task 3" %}
In this task you just have to update the value of the state variables. An other way to understand the state variable concept is just to understand that they are the static ones that can be used the the next call of the function to recall the former values.

```python
# the process function!
def process(input_buffer, output_buffer, buffer_len):
    # specify global variables modified here
    global y, x

    # process one sample at a time
    for n in range(buffer_len):

        # apply input gain
        x[0] = int(GAIN * input_buffer[n])

        # compute filter output
        output_buffer[n] = int(b_coef[0] * x[0] / HALF_MAX_VAL)
        for i in range(1, N_COEF):

            output_buffer[n] += int((b_coef[i] * x[i] / HALF_MAX_VAL) - (a_coef[i] * y[i] / HALF_MAX_VAL))

        # update state variables
        y[0] = output_buffer[n]
        for i in reversed(range(1, N_COEF)):
            x[i] = x[i-1]
            y[i] = y[i-1
```
{% endtab %}

{% tab title="Task 4" %}
The first task is to compute the contribution made from the past input variables to the intermediate signal called $$w[n]$$.

```python
# the process function!
def process(input_buffer, output_buffer, buffer_len):

    # specify global variables modified here
    global w

    # process one sample at a time
    for n in range(buffer_len):

        # apply input gain
        w[0] = int(GAIN * input_buffer[n])

        # compute contribution from state variables
        for i in range(1, N_COEF):
            w[0] -= int(a_coef[i]/HALF_MAX_VAL*w[i])
```
{% endtab %}

{% tab title="Task 5" %}
The second step is to compute the output signal from $$w[n]$$ that we just computed.

```python
# the process function!
def process(input_buffer, output_buffer, buffer_len):

    # specify global variables modified here
    global w

    # process one sample at a time
    for n in range(buffer_len):

        # apply input gain
        w[0] = int(GAIN * input_buffer[n])

        # compute contribution from state variables
        for i in range(1, N_COEF):
            w[0] -= int(a_coef[i]/HALF_MAX_VAL*w[i])

        # compute output
        output_buffer[n] = 0
        for i in range(N_COEF):
            output_buffer[n] += int(b_coef[i]/HALF_MAX_VAL*w[i])
```
{% endtab %}

{% tab title="Task 6" %}
Lastly we can update the state variable.

```python
# the process function!
def process(input_buffer, output_buffer, buffer_len):

    # specify global variables modified here
    global w

    # process one sample at a time
    for n in range(buffer_len):

        # apply input gain
        w[0] = int(GAIN * input_buffer[n])

        # compute contribution from state variables
        for i in range(1, N_COEF):
            w[0] -= int(a_coef[i]/HALF_MAX_VAL*w[i])

        # compute output
        output_buffer[n] = 0
        for i in range(N_COEF):
            output_buffer[n] += int(b_coef[i]/HALF_MAX_VAL*w[i])

        # update state variables
        for i in reversed(range(1, N_COEF)):
            w[i] = w[i-1]
```
{% endtab %}

{% tab title="Task 7" %}
To test the biquad implementation withe the sounddevice template, you just have to use the same process function that was made in the previous steps and use the sounddevice template.

We propose you a _C_ version of the direct form 1 of the filter. There is some variable changes but it is the same process:

```c
// the process function!
void inline process(int16_t *bufferInStereo, int16_t *bufferOutStereo, uint16_t size) {

    int16_t x[FRAME_PER_BUFFER];
    int16_t y[FRAME_PER_BUFFER];
    int32_t ACC;

    for(int i = 0; i<FRAME_PER_BUFFER;i++){
        y[i] = 0;
    }

#define GAIN 8         // We loose 1us if we use 10 in stead of 8

    // Take signal from left side
    for (uint16_t i = 0; i < size; i += 2) {
        x[i / 2] = bufferInStereo[i];
    }

    // High pass filtering
    for (uint i = 0; i < FRAME_PER_BUFFER; i++) {

        x_old[ix++] = x[i];
        ix %= num_coefs;

        ACC = 0;
        for(int j = 0; j < num_coefs; j++){
            ACC += ((int32_t)x_old[(ix+j) % num_coefs] * coefs_b[num_coefs-j-1]) / half_MAX_INT16;
            ACC += ((int32_t)y_old[(iy+j+1) % num_coefs] * coefs_a[num_coefs-j-1]) / half_MAX_INT16;
        }
        y[i] = y_old[iy++] = (int32_t) ACC;
        iy %= num_coefs;
        y[i] *= GAIN;
    }

    // Interleaved left and right
    for (uint16_t i = 0; i < size; i += 2) {
        bufferOutStereo[i] = (int16_t) y[i / 2];
        // Put signal on both side
        bufferOutStereo[i + 1] = (int16_t) y[i / 2];
    }
}
```
{% endtab %}
{% endtabs %}

